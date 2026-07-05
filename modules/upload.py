"""Upload module — fetch remote file to agent."""
import os, time
def run(args):
    url = args.get('url') or args.get('source')
    dest = args.get('destination') or args.get('dest', '/tmp/uploaded_' + str(int(time.time())))
    if not url:
        return {'status': 'queued', 'destination': dest, 'type': 'upload', 'note': 'download to ' + dest}
    try:
        from urllib.request import urlopen
        with urlopen(url, timeout=15) as r, open(dest, 'wb') as f:
            f.write(r.read())
        return {'status': 'uploaded', 'destination': dest, 'type': 'upload', 'size': os.path.getsize(dest)}
    except ImportError:
        return {'status': 'queued', 'destination': dest, 'type': 'upload', 'note': 'requires urllib on agent'}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'destination': dest, 'type': 'upload'}
