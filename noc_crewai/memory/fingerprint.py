import hashlib

def compute_fingerprint(service: str, alert_type: str, root_cause: str) -> str:
    raw = f"{service}:{alert_type}:{root_cause}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()
