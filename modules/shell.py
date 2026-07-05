"""Shell module — execute command string."""
def run(args):
    cmd = args.get('command') or args.get('args', ['whoami'])[0]
    import subprocess
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60, text=True, errors='replace')
        return {'output': out, 'type': 'shell'}
    except Exception as e:
        return {'output': '', 'error': str(e), 'type': 'shell'}
