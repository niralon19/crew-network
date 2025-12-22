import json
import types
import pytest

from noc_crewai.models import Alert, Conclusion, Finding, Evidence
from noc_crewai.memory.store import IncidentStore
from noc_crewai.main import handle_alert
class DummyJira:
    def __init__(self):
        self.created = []
    def create_issue(self, **kwargs):
        self.created.append(kwargs)
        return {"key": "OPS-1"}

@pytest.fixture
def store(tmp_path):
    return IncidentStore(str(tmp_path / "mem.db"))

def test_flow_new_incident(monkeypatch, store):
    # Mock build_agents to avoid real CrewAI/LLM
    def fake_build_agents():
        return {
            "coatr": object(),
            "traffic": object(),
            "coupling": object(),
            "conclusion": object(),
        }

    # Router deterministic
    monkeypatch.setattr("noc_crewai.main.build_agents", fake_build_agents)

    # Mock domain investigation to return deterministic finding/evidence
    def fake_run_domain_investigation(alert, route, agent):
        return (
            Finding(agent=route, finding="DB pool exhausted", confidence="high"),
            Evidence(logs=["pool exhausted"], metrics={"error_rate": 7.2}, sql={"rowcount": 1}),
        )
    monkeypatch.setattr("noc_crewai.main.run_domain_investigation", fake_run_domain_investigation)

    # Mock conclude to return normalized root cause
    def fake_conclude(alert, findings, evidence, conclusion_agent):
        return Conclusion(
            summary="DB pool exhaustion during traffic spike",
            root_cause="db_connection_pool_exhaustion",
            why_it_happened=["traffic spike", "pool too small"],
            actions={"immediate": ["increase pool"], "short_term": [], "long_term": []},
            ownership={"team": "Backend", "priority": "P1"},
            confidence="high",
            requires_human_approval=True,
        )
    monkeypatch.setattr("noc_crewai.main.conclude", fake_conclude)

    # Mock publish_to_jira to avoid requests
    def fake_publish_to_jira(alert, conclusion, jira):
        return "OPS-1"
    monkeypatch.setattr("noc_crewai.main.publish_to_jira", fake_publish_to_jira)

    alert = Alert(
        id="a1", type="coatr", service="coatr-api", description="err", severity="critical",
        timestamp="2025-12-22T00:00:00Z", metadata={}
    )
    result = handle_alert(alert, store=store, jira=DummyJira())

    assert result["memory"]["result"] == "new_incident"
    assert result["memory"]["jira_key"] == "OPS-1"

def test_flow_duplicate(monkeypatch, store):
    # Same mocks as above
    def fake_build_agents():
        return {"coatr": object(), "traffic": object(), "coupling": object(), "conclusion": object()}
    monkeypatch.setattr("noc_crewai.main.build_agents", fake_build_agents)

    def fake_run_domain_investigation(alert, route, agent):
        return (Finding(agent=route, finding="DB pool exhausted", confidence="high"), Evidence())
    monkeypatch.setattr("noc_crewai.main.run_domain_investigation", fake_run_domain_investigation)

    def fake_conclude(alert, findings, evidence, conclusion_agent):
        return Conclusion(
            summary="same",
            root_cause="db_connection_pool_exhaustion",
            why_it_happened=[],
            actions={"immediate": [], "short_term": [], "long_term": []},
            ownership={"team": "Backend", "priority": "P1"},
            confidence="high",
            requires_human_approval=True,
        )
    monkeypatch.setattr("noc_crewai.main.conclude", fake_conclude)
    monkeypatch.setattr("noc_crewai.main.publish_to_jira", lambda a,c,j: "OPS-1")

    alert1 = Alert(id="a1", type="coatr", service="coatr-api", description="err", severity="critical",
                   timestamp="2025-12-22T00:00:00Z", metadata={})
    alert2 = Alert(id="a2", type="coatr", service="coatr-api", description="err2", severity="critical",
                   timestamp="2025-12-22T00:05:00Z", metadata={})

    r1 = handle_alert(alert1, store=store, jira=DummyJira())
    r2 = handle_alert(alert2, store=store, jira=DummyJira())

    assert r1["memory"]["result"] == "new_incident"
    assert r2["memory"]["result"] == "duplicate"
    assert r2["memory"]["jira_key"] == "OPS-1"
