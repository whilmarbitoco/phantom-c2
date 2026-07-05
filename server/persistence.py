"""Persistence layer for Phantom C2 — SQLite."""
import sqlite3, json, time
from contextlib import contextmanager

class Persistence:
    def __init__(self, path='phantom.db'):
        self.path = path
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.path, check_same_thread=False)

    def _init_db(self):
        q = self._conn()
        q.executescript('''
        CREATE TABLE IF NOT EXISTS agents (aid TEXT PRIMARY KEY, info TEXT, registered_at REAL, last_seen REAL);
        CREATE TABLE IF NOT EXISTS commands (cid TEXT PRIMARY KEY, aid TEXT, cmd TEXT, args TEXT, module TEXT, data TEXT, status TEXT, created REAL, completed REAL, result TEXT);
        CREATE TABLE IF NOT EXISTS results (rid INTEGER PRIMARY KEY AUTOINCREMENT, aid TEXT, cid TEXT, payload TEXT, received_at REAL);
        ''')
        q.commit(); q.close()

    @contextmanager
    def cursor(self):
        q = self._conn(); c = q.cursor()
        try: yield c; q.commit()
        finally: c.close(); q.close()

    def save_agent(self, aid, info):
        with self.cursor() as c:
            c.execute('INSERT OR REPLACE INTO agents VALUES (?,?,?,?)',
                      (aid, json.dumps(info), info.get('registered_at', time.time()), info.get('last_seen', time.time())))

    def save_command(self, aid, cid, cmd):
        with self.cursor() as c:
            c.execute('INSERT OR REPLACE INTO commands VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (cid, aid, cmd.get('cmd'), json.dumps(cmd.get('args', [])), cmd.get('module'), json.dumps(cmd.get('data') or {}), 'pending', time.time(), None, None))

    def update_command_status(self, cid, status, result=None):
        with self.cursor() as c:
            c.execute('UPDATE commands SET status=?, completed=?, result=? WHERE cid=?',
                      (status, time.time(), json.dumps(result) if result else None, cid))

    def save_result(self, aid, cid, data):
        with self.cursor() as c:
            c.execute('INSERT INTO results (aid,cid,payload,received_at) VALUES (?,?,?,?)',
                      (aid, cid, json.dumps(data), data.get('received_at', time.time())))

    def get_results(self, aid):
        q = self._conn(); c = q.cursor()
        c.execute('SELECT payload FROM results WHERE aid=? ORDER BY received_at DESC LIMIT 200', (aid,))
        rows = [json.loads(r[0]) for r in c.fetchall()]; c.close(); q.close()
        return rows
