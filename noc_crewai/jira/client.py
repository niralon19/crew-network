import requests
from requests.auth import HTTPBasicAuth

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str, project_key: str):
        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(email, api_token)
        self.project_key = project_key
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def create_issue(self, *, summary: str, description: str, issue_type: str = "Task",
                     priority: str = "High", labels: list[str] | None = None) -> dict:
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
                "labels": labels or [],
            }
        }
        resp = requests.post(
            f"{self.base_url}/rest/api/3/issue",
            headers=self.headers,
            auth=self.auth,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
