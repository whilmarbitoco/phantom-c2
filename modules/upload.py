"""Upload file to agent."""
def run(args):
    dest = args.get('destination', '/tmp/uploaded')
    return {'status': 'queued', 'destination': dest, 'type': 'upload', 'note': 'Requires server-to-agent transfer channel'}
