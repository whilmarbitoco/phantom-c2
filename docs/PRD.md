# Phantom C2 — Product Requirements Document

> CTF and authorized testing only. Unauthorized access is illegal.

## 1. Vision

Phantom C2 is a terminal-first, retro-hacker styled command-and-control platform built for red teaming, capture the flag, and authorized security research. The interface should evoke the Mr. Robot aesthetic: dark, minimal, terminal-driven, with real-time agent feeds and a sense of operational control.

## 2. Goals

1. Provide a functional C2 server with real command dispatch, result collection, and agent lifecycle management.
2. Deliver a browser-based dashboard that looks and feels like a hacker terminal — not a corporate admin panel.
3. Support modular post-exploitation tasks: shell, screenshot, keylogger, webcam, persistence, privilege escalation, reconnaissance, credential harvest, file manager, upload, download.
4. Keep everything in Python for portability and hackathon speed.
5. Avoid minimal toy implementations. The UI must feel like a real ops center.

## 3. Non-Goals

- No kernel-level rootkits or kernel exploits.
- No C2 over DNS, ICMP, or exotic covert channels in MVP.
- No mobile agent or cross-compilation chains in MVP.
- No production hardening or anonymity routing in MVP.

## 4. Architecture

```
phantom-c2/
  server/
    app.py               # Flask + Socket.IO backend
    c2_api.py            # REST API routes
    agent_manager.py     # Agent registry, polling, heartbeat
    module_loader.py     # Module definitions and execution engine
    persistence.py       # Save/load operations, database
    build_agent.py       # Agent binary builder
  agent/
    phantom_agent.py     # Agent polling agent
  modules/
    shell.py
    screenshot.py
    keylogger.py
    webcam.py
    persist.py
    elevate.py
    recon.py
    creds.py
    files.py
    upload.py
    download.py
  static/
    css/
      terminal.css
      matrix.css
    js/
      terminal.js
      socket.js
      agents.js
  templates/
    terminal.html
    agent_detail.html
  docs/
    PRD.md
    ARCHITECTURE.md
```

## 5. Functional Requirements

### 5.1 Server
- [ ] Agent registration with metadata collection.
- [ ] Poll-based command delivery with configurable interval.
- [ ] Command queue per agent with status tracking.
- [ ] Result storage with timestamping.
- [ ] WebSocket real-time event broadcasting.
- [ ] Module registry with descriptions and parameters.
- [ ] Agent builder that generates configured agent scripts as ZIP.
- [ ] Persistence layer for agents, commands, results, and modules.
- [ ] Health endpoint and basic logging.

### 5.2 Dashboard
- [ ] Terminal-style layout with ASCII banner.
- [ ] Agent list panel with status, OS, hostname, last seen.
- [ ] Per-agent terminal view with command input and output stream.
- [ ] Module picker with parameter forms.
- [ ] Live event log scrolling like a syslog feed.
- [ ] Responsive layout with monospace fonts and scanline effects.

### 5.3 Agent
- [ ] Beacon polling to /api/agent/<id>/poll.
- [ ] Command execution with timeout and error capture.
- [ ] Result POST back to /api/agent/<id>/result/<cid>.
- [ ] Auto-reconnect on server loss.
- [ ] Configurable C2 URL and poll interval.

### 5.4 Modules
- [ ] shell — execute arbitrary command string.
- [ ] screenshot — capture display to image.
- [ ] keylogger — start/stop keystroke capture.
- [ ] webcam — capture webcam image.
- [ ] persist — install persistence mechanism.
- [ ] elevate — attempt privilege escalation.
- [ ] recon — enumerate host, user, network, privileges.
- [ ] creds — harvest stored credentials.
- [ ] files — list, read, delete files.
- [ ] upload — upload file to agent.
- [ ] download — download file from agent.

## 6. Non-Functional Requirements

- [ ] Performance — polling interval configurable between 1–30 seconds.
- [ ] Reliability — command queue persists across server restarts.
- [ ] Scalability — support 50+ concurrent agents in MVP.
- [ ] Security — operations must be restricted to authorized environments.
- [ ] Availability — server should run unattended with basic logging.
- [ ] Low bandwidth — polling payload minimized; results compressed.

## 7. UI / Aesthetic Requirements

### Mr. Robot Styling
- [ ] Dark backgrounds: #050505, #0a0a0a, #111.
- [ ] Accent colors: dark green #0f0, amber #ffb000, red #ff003c.
- [ ] Fonts: JetBrains Mono or Fira Code, 13–14px base.
- [ ] Scanline overlay: semi-transparent repeating linear gradient.
- [ ] Terminal prompt style: `root@phantom:~#` or `elliot@fsociety:~$`.
- [ ] ASCII art logo: `Phantom C2` with glitched block letters.
- [ ] Subtle CRT flicker animation on load.
- [ ] Status indicators as blinking dots or spinning brackets.
- [ ] Event log with timestamps in `[HH:MM:SS]` format.

### Layout
- [ ] Top bar: logo, server status, connected agents count, uptime.
- [ ] Left panel: agent list with compact cards.
- [ ] Center: active agent terminal with command input.
- [ ] Right panel: module list and module parameter form.
- [ ] Bottom panel: live event log.

## 8. Technical Stack

- [ ] Backend: Python 3.10+, Flask, Flask-SocketIO.
- [ ] Frontend: HTML5, CSS3, vanilla JavaScript, Socket.IO client.
- [ ] Agent: Python standard library only, no external dependencies.
- [ ] Persistence: SQLite via SQLAlchemy or plain JSON files.
- [ ] Real-time: WebSocket via Flask-SocketIO.

## 9. Command Protocol

### Register
POST /api/register
Body: { id?, hostname, username, os, arch, privileges }

### Poll
GET /api/agent/<id>/poll
Response: { commands: { <cid>: { cmd, args, module?, data? } } }

### Result
POST /api/agent/<id>/result/<cid>
Body: { output, type?, files?, error? }

## 10. Success Criteria

- [ ] A judge can launch the server, build an agent, and see a connected agent within 60 seconds.
- [ ] Shell commands execute and show results in the terminal in real time.
- [ ] Screenshot module captures and displays an image in the dashboard.
- [ ] The UI passes the “looks like Mr. Robot” test on first impression.
- [ ] All module stubs exist and show expected status messages even if OS-specific capture is limited.

## 11. Out of Scope for v1

- Multi-user authentication and RBAC.
- Encrypted covert channels.
- Mobile agents.
- Distributed C2 pools.
- Payload obfuscation or AV evasion.

## 12. Milestones

| Milestone | Deliverable |
|---|---|
| M1 | Server core: registration, polling, command dispatch, persistence |
| M2 | Dashboard: agent list, terminal, modules, events |
| M3 | Modules: shell, recon, screenshot |
| M4 | Stub modules: keylogger, webcam, persist, elevate, creds, files, upload, download |
| M5 | Agent builder, packaging, README with legal disclaimers |
| M6 | Styling polish, scanlines, font tuning, ASCII logo |
