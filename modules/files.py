"""File manager."""
import os
def run(args):
    path = args.get('path', '.')
    action = args.get('action', 'list')
    try:
        if action == 'list':
            entries = os.listdir(path)
            return {'output': '\n'.join(entries), 'type': 'files'}
        if action == 'read':
            with open(path, 'r', errors='replace') as f:
                return {'output': f.read()[:4000], 'type': 'files'}
        return {'status': 'ok', 'type': 'files'}
    except Exception as e:
        return {'error': str(e), 'type': 'files'}
