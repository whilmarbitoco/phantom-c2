"""Screenshot module — real capture if pyscreenshot/pillow available, else stub."""
import os, time
def run(args):
    try:
        try:
            import pyscreenshot as ImageGrab
            img = ImageGrab.grab()
            path = '/tmp/screenshot_' + str(int(time.time())) + '.png'
            img.save(path)
            return {'status': 'captured', 'filename': path, 'type': 'screenshot', 'size': os.path.getsize(path)}
        except ImportError:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            path = '/tmp/screenshot_' + str(int(time.time())) + '.png'
            img.save(path)
            return {'status': 'captured', 'filename': path, 'type': 'screenshot', 'size': os.path.getsize(path)}
    except ImportError:
        return {'status': 'stub', 'filename': 'screen.png', 'type': 'screenshot', 'note': 'install pyscreenshot or pillow for capture'}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'type': 'screenshot'}
