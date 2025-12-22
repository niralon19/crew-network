from ..models import Alert, Conclusion
from ..policy import should_open_jira
from .formatter import format_description
from .client import JiraClient

PRIORITY_MAP = {
    "P0": "Highest",
    "P1": "High",
    "P2": "Medium",
}

def publish_to_jira(alert: Alert, conclusion: Conclusion, jira: JiraClient) -> str | None:
    if not should_open_jira(conclusion):
        return None

    priority = PRIORITY_MAP.get((conclusion.ownership or {}).get("priority", "P2"), "Medium")
    labels = ["ai-incident", f"service-{alert.service.lower()}"]

    description = format_description(alert, conclusion)
    issue = jira.create_issue(
        summary=conclusion.summary[:240],
        description=description,
        issue_type="Task",
        priority=priority,
        labels=labels,
    )
    return issue.get("key")
