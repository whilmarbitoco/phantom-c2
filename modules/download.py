"""Download file from agent."""
def run(args):
    src = args.get('source', '/etc/passwd')
    return {'status': 'queued', 'source': src, 'type': 'download', 'note': 'Requires server-to-agent transfer channel'}
