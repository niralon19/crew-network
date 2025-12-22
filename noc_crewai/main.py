from __future__ import annotations
import os
from dotenv import load_dotenv

from .models import Alert, Evidence
from .router import route_alert
from .agents import build_agents
from .domain_runner import run_domain_investigation
from .conclusion import conclude
from .jira.client import JiraClient
from .jira.publisher import publish_to_jira
from .memory.store import IncidentStore
from .memory.dedup import process_conclusion_with_memory
from .memory.ttl import cleanup_closed

def _build_jira_from_env() -> JiraClient | None:
    base = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    proj = os.getenv("JIRA_PROJECT_KEY")
    if not all([base, email, token, proj]):
        return None
    return JiraClient(base, email, token, proj)

def handle_alert(alert: Alert, *, store: IncidentStore, jira: JiraClient | None = None) -> dict:
    agents = build_agents()

    route = route_alert(alert)
    domain_agent = agents[route]
    finding, evidence = run_domain_investigation(alert, route, domain_agent)

    # Merge evidence (single domain in this version)
    merged_evidence = evidence if isinstance(evidence, Evidence) else Evidence()

    conclusion = conclude(alert, [finding], merged_evidence, agents["conclusion"])

    jira_key = None
    if jira is not None:
        jira_key = publish_to_jira(alert, conclusion, jira)

    mem = process_conclusion_with_memory(
        store=store,
        alert=alert,
        conclusion=conclusion,
        jira_key=jira_key,
    )

    return {
        "route": route,
        "finding": finding.model_dump(),
        "evidence": merged_evidence.model_dump(),
        "conclusion": conclusion.model_dump(),
        "memory": mem,
    }

def sample_alert() -> Alert:
    return Alert(
        id="grafana-123",
        type="coatr",
        service="coatr-api",
        description="5xx spike above threshold",
        severity="critical",
        timestamp="2025-12-22T13:40:00Z",
        metadata={"grafana_url": "https://grafana.example/...", "error_rate": 7.2},
    )

def main():
    load_dotenv()

    store = IncidentStore(os.getenv("INCIDENT_DB_PATH", "incident_memory.db"))
    cleanup_closed(store, hours=int(os.getenv("INCIDENT_TTL_HOURS", "24")))

    jira = _build_jira_from_env()

    alert = sample_alert()
    result = handle_alert(alert, store=store, jira=jira)
    print(result)

if __name__ == "__main__":
    main()
