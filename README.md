# Phantom C2

**CTF / authorized testing only. Unauthorized access is illegal.**

## Run
```bash
python server/app.py
# open http://localhost:8080
```

## Build agent
From build tab or:
```bash
curl "http://localhost:8080/api/build/agent?c2_url=http://<server-ip>:8080&poll_interval=5" -o agent.zip
python agent/phantom_agent.py --c2 http://server:8080
```

## Stack
- Backend: Python + Flask + Flask-SocketIO
- Frontend: vanilla JS + Socket.IO client, terminal UI
- Agent: Python stdlib only, no installs
- Persistence: SQLite in `phantom.db`

## Disclaimer
Use only against systems you own or have explicit permission to test.
