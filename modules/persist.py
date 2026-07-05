"""Persistence module."""
import os
def run(args):
    method = args.get('method', 'registry')
    return {'status': 'installed', 'method': method, 'type': 'persist', 'platform': 'windows' if os.name == 'nt' else 'linux'}
