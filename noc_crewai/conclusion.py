import json
from crewai import Crew
from .tasks import conclusion_task
from .models import Alert, Finding, Evidence, Conclusion

def conclude(alert: Alert, findings: list[Finding], evidence: Evidence, conclusion_agent) -> Conclusion:
    context = {
        "alert": alert.model_dump(),
        "findings": [f.model_dump() for f in findings],
        "evidence": evidence.model_dump(),
    }
    context_json = json.dumps(context, ensure_ascii=False)

    task = conclusion_task(conclusion_agent, context_json)
    crew = Crew(agents=[conclusion_agent], tasks=[task], verbose=True)
    output = crew.kickoff()

    try:
        data = json.loads(str(output))
        return Conclusion(**data)
    except Exception:
        # Hard fail-safe: never crash the pipeline for summary.
        return Conclusion(
            summary=str(output),
            root_cause="unknown",
            why_it_happened=[],
            actions={"immediate": [], "short_term": [], "long_term": []},
            ownership={"team": "NOC", "priority": "P2"},
            confidence="low",
            requires_human_approval=True,
        )
