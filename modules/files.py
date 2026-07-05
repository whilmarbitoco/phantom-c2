"""File manager module."""
import os, json
def run(args):
    path = args.get('path', '.')
    action = args.get('action', 'list')
    depth = int(args.get('depth', 1))
    try:
        if action == 'list':
            entries = []
            for name in os.listdir(path):
                full = os.path.join(path, name)
                try:
                    st = os.stat(full)
                    entries.append({'name': name, 'path': full, 'is_dir': os.path.isdir(full), 'size': st.st_size, 'mtime': st.st_mtime})
                except Exception:
                    entries.append({'name': name, 'path': full, 'error': 'stat failed'})
            lines = []
            for e in entries[:50]:
                kind = 'DIR' if e.get('is_dir') else 'FILE'
                lines.append(f"{kind:4}  {e.get('size',0):>10}  {e['name']}")
            return {'output': '\n'.join(lines), 'type': 'files', 'count': len(entries)}
        if action == 'read':
            with open(path, 'r', errors='replace') as f:
                data = f.read(4000)
            return {'output': data, 'type': 'files', 'path': path}
        if action == 'find':
            q = args.get('query', '').lower()
            if not q:
                return {'output': 'query required', 'type': 'files'}
            matches = []
            for root, dirs, files in os.walk(path):
                for fn in files:
                    if q in fn.lower():
                        matches.append(os.path.join(root, fn))
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                if len(matches) >= 50:
                    break
            return {'output': '\n'.join(matches[:50]), 'type': 'files', 'count': len(matches)}
        return {'output': 'unknown action', 'type': 'files', 'error': True}
    except Exception as e:
        return {'output': '', 'error': str(e), 'type': 'files'}
