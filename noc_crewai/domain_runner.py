import json
from crewai import Crew
from .tasks import domain_task
from .models import Alert, Finding, Evidence

def run_domain_investigation(alert: Alert, route: str, agent) -> tuple[Finding, Evidence]:
    # LLM is used here via CrewAI agent reasoning + tool calls.
    task = domain_task(agent, alert, route)
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    output = crew.kickoff()

    # We expect agent returns JSON; but we harden parsing.
    finding_text = ""
    confidence = "medium"
    evidence = Evidence()

    try:
        data = json.loads(str(output))
        finding_text = data.get("finding") or data.get("result") or str(output)
        confidence = data.get("confidence", confidence)
        ev = data.get("evidence", {})
        evidence = Evidence(
            logs=list(ev.get("logs", [])),
            metrics=dict(ev.get("metrics", {})),
            sql=dict(ev.get("sql", {})),
        )
    except Exception:
        finding_text = str(output)

    return Finding(agent=route, finding=finding_text, confidence=confidence), evidence
