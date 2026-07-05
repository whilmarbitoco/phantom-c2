"""Reconnaissance module — collects system information."""
import platform, os, socket, json, time
def run(args):
    info = {
        'hostname': platform.node(),
        'user': os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
        'os': platform.system() + ' ' + platform.release() + ' ' + platform.version(),
        'arch': platform.machine(),
        'processor': platform.processor(),
        'privileges': 'admin' if os.name == 'nt' else 'root' if hasattr(os, 'geteuid') and os.geteuid() == 0 else 'user',
        'pid': os.getpid(),
        'cwd': os.getcwd(),
        'home': os.path.expanduser('~'),
        'ip': socket.gethostbyname(socket.gethostname()) if socket.gethostname() else 'unknown',
        'timestamp': time.time()
    }
    return {'output': json.dumps(info, indent=2), 'type': 'recon'}
