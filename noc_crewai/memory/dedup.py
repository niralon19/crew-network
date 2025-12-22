from datetime import datetime
from .fingerprint import compute_fingerprint
from .store import IncidentStore
from ..models import Alert, Conclusion

def process_conclusion_with_memory(
    *,
    store: IncidentStore,
    alert: Alert,
    conclusion: Conclusion,
    jira_key: str | None,
) -> dict:
    fingerprint = compute_fingerprint(alert.service, alert.type, conclusion.root_cause)

    existing = store.get(fingerprint)
    if existing:
        store.touch(fingerprint)
        return {
            "result": "duplicate",
            "fingerprint": fingerprint,
            "jira_key": existing["jira_key"],
        }

    store.create(
        fingerprint=fingerprint,
        service=alert.service,
        alert_type=alert.type,
        root_cause=conclusion.root_cause,
        jira_key=jira_key,
    )
    return {
        "result": "new_incident",
        "fingerprint": fingerprint,
        "jira_key": jira_key,
    }
