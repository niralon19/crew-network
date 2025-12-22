from datetime import datetime, timedelta
from .store import IncidentStore

def cleanup_closed(store: IncidentStore, hours: int = 24) -> int:
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    cur = store.conn.execute(
        "DELETE FROM incidents WHERE status='closed' AND last_seen < ?",
        (cutoff,),
    )
    return cur.rowcount
