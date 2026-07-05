"""Persistence / autorun module."""
import os, sys, platform
def run(args):
    method = args.get('method', 'registry') if isinstance(args, dict) else 'registry'
    system = platform.system()
    if system == 'Windows':
        return {'status': 'installed', 'method': method, 'type': 'persist', 'platform': 'windows', 'location': 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'}
    return {'status': 'installed', 'method': method, 'type': 'persist', 'platform': system, 'location': '/etc/rc.local or crontab', 'note': 'requires sudo for system-wide persistence'}
