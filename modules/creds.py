"""Credential harvest."""
def run(args):
    return {'status': 'harvested', 'target': args.get('target', 'browser'), 'type': 'creds', 'count': 0, 'note': 'stub'}
