from crewai import Task

def domain_task(agent, alert, route: str) -> Task:
    return Task(
        agent=agent,
        description=f"""
        You are handling a production alert.

        Route: {route}
        Alert ID: {alert.id}
        Service: {alert.service}
        Severity: {alert.severity}
        Description: {alert.description}
        Metadata: {alert.metadata}

        Use ONLY your available tools to gather evidence.
        Provide a concise finding and confidence.
        Return JSON with fields: finding, confidence, evidence (metrics/logs/sql).
        """,
        expected_output="JSON with finding/confidence/evidence"
    )

def conclusion_task(agent, context_json: str) -> Task:
    return Task(
        agent=agent,
        description=f"""
        You are given verified findings and evidence from domain agents.

        Context JSON:
        {context_json}

        Produce STRICT JSON with:
        - summary
        - root_cause (normalized short string)
        - why_it_happened (list)
        - actions: immediate, short_term, long_term (each list)
        - ownership: team, priority (P0/P1/P2)
        - confidence (low/medium/high)
        - requires_human_approval (bool)

        Do not invent evidence. If insufficient, set confidence=low and actions empty.
        """,
        expected_output="Strict JSON conclusion"
    )
