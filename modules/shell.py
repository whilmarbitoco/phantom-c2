"""Interactive shell module — execute command string."""
import subprocess, shlex
def run(args):
    cmd = args.get('command') or args.get('args')
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)
    if not cmd:
        return {'output': 'no command provided', 'type': 'shell', 'error': True}
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=60,
            text=True,
            errors='replace'
        )
        out = result.stdout
        err = result.stderr
        return {
            'output': out + (f'\n[STDERR]\n{err}' if err else ''),
            'type': 'shell',
            'rc': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'output': '', 'error': 'command timed out after 60s', 'type': 'shell'}
    except Exception as e:
        return {'output': '', 'error': str(e), 'type': 'shell'}
