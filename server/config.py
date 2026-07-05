"""Phantom C2 configuration."""
import os
HOST = os.environ.get('PHANTOM_HOST', '0.0.0.0')
PORT = int(os.environ.get('PHANTOM_PORT', 8080))
DB_PATH = os.environ.get('PHANTOM_DB', 'phantom.db')
