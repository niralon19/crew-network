from crewai import Agent
from .tools.traffic import check_traffic
from .tools.metrics import check_ratios
from .tools.logs import analyze_logs
from .tools.db import run_sql

def build_agents():
    traffic_agent = Agent(
        role="Traffic Integrity Specialist",
        goal="Verify traffic integrity and detect anomalies",
        backstory="Senior NOC engineer specializing in network traffic analysis",
        tools=[check_traffic],
        verbose=True,
    )

    coupling_agent = Agent(
        role="Coupling & Ratios Specialist",
        goal="Validate system ratios and percentage-based metrics",
        backstory="SRE focused on SLIs, ratios, and drift detection",
        tools=[check_ratios],
        verbose=True,
    )

    coatr_agent = Agent(
        role="Application & DB Specialist",
        goal="Investigate application issues using logs and SQL",
        backstory="Backend engineer with deep observability experience",
        tools=[analyze_logs, run_sql],
        verbose=True,
    )

    conclusion_agent = Agent(
        role="Operations Conclusion Specialist",
        goal="Produce clear root cause analysis and actionable remediation steps",
        backstory="Senior SRE specializing in post-incident analysis and prevention",
        verbose=True,
    )

    return {
        "traffic": traffic_agent,
        "coupling": coupling_agent,
        "coatr": coatr_agent,
        "conclusion": conclusion_agent,
    }
