"""Agent registry, heartbeat, and command queue."""
import time
from persistence import Persistence

class AgentManager:
    def __init__(self, persist: Persistence, socketio=None):
        self.persist = persist
        self.socketio = socketio
        self.agents = {}
        self.command_queues = {}

    def register(self, aid, info):
        info.setdefault('registered_at', time.time())
        info['last_seen'] = time.time()
        info['connected'] = True
        info['status'] = 'active'
        self.agents[aid] = info
        self.command_queues.setdefault(aid, {})
        self.persist.save_agent(aid, info)
        if self.socketio:
            self.socketio.emit('agent_connected', self.get_agent(aid))
            self.socketio.emit('event', {'ts': time.strftime('%H:%M:%S'), 'type': 'connect', 'aid': aid, 'text': f'Agent {aid} connected'})

    def issue_command(self, aid, cid, cmd):
        self.command_queues.setdefault(aid, {})[cid] = {'cmd': cmd, 'status': 'pending', 'created': time.time()}

    def pending_commands(self, aid):
        return {cid: cmd for cid, cmd in self.command_queues.get(aid, {}).items() if cmd['status'] == 'pending'}

    def complete_command(self, aid, cid):
        if aid in self.command_queues and cid in self.command_queues[aid]:
            self.command_queues[aid][cid]['status'] = 'completed'
        if aid in self.agents:
            self.agents[aid]['last_seen'] = time.time()

    def list_agents(self):
        return list(self.agents.values())

    def get_agent(self, aid):
        return self.agents.get(aid)
