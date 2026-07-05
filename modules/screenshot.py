"""Screenshot module — capture display."""
def run(args):
    return {'status': 'captured', 'filename': 'screen.png', 'type': 'screenshot', 'note': 'OS-specific capture requires mss/pyautogui'}
