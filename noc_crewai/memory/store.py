import sqlite3
from datetime import datetime

class IncidentStore:
    def __init__(self, db_path: str = "incident_memory.db"):
        self.conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS incidents (
            fingerprint TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            root_cause TEXT NOT NULL,
            status TEXT CHECK(status IN ('open','mitigated','closed')) NOT NULL,
            jira_key TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_incidents_service ON incidents(service);
        CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
        """)

    def get(self, fingerprint: str):
        cur = self.conn.execute("SELECT * FROM incidents WHERE fingerprint = ?", (fingerprint,))
        return cur.fetchone()

    def create(self, *, fingerprint: str, service: str, alert_type: str, root_cause: str, jira_key: str | None):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO incidents VALUES (?, ?, ?, ?, 'open', ?, ?, ?)",
            (fingerprint, service, alert_type, root_cause, jira_key, now, now),
        )

    def touch(self, fingerprint: str):
        now = datetime.utcnow().isoformat()
        self.conn.execute("UPDATE incidents SET last_seen = ? WHERE fingerprint = ?", (now, fingerprint))

    def update_status(self, fingerprint: str, status: str):
        self.conn.execute("UPDATE incidents SET status = ? WHERE fingerprint = ?", (status, fingerprint))
