# Architecture 3D — noc_crewai

להלן תצוגה “3D” סכמטית (קופסאות עומק) + תרשים זרימה Mermaid.

```text
             ┌───────────────────────────────────────────────┐
             │                 External World                 │
             │───────────────────────────────────────────────│
             │ Grafana Alerts / Prometheus / Loki / DB / etc │
             └───────────────▲───────────────────────────────┘
                             │
                             │  Alert (structured)
                             │
        ┌────────────────────┴───────────────────────────────┐
        │                     Runtime Pod                     │
        │─────────────────────────────────────────────────────│
        │  ┌───────────────────────────────────────────────┐  │
        │  │  1) Router (deterministic)                    │  │
        │  └───────────────▲───────────────────────────────┘  │
        │                  │ route                            │
        │  ┌───────────────┴───────────────────────────────┐  │
        │  │  2) Domain Crew (LLM reasoning + tools)       │  │
        │  │     - Traffic Agent                           │  │
        │  │     - Coupling Agent                          │  │
        │  │     - COATR App/DB Agent                      │  │
        │  └───────────────▲───────────────────────────────┘  │
        │                  │ findings/evidence                │
        │  ┌───────────────┴───────────────────────────────┐  │
        │  │  3) Conclusion Agent (LLM synthesis)           │  │
        │  └───────────────▲───────────────────────────────┘  │
        │                  │ conclusion JSON                  │
        │  ┌───────────────┴───────────────────────────────┐  │
        │  │  4) Memory + Policy (NO LLM)                   │  │
        │  │     - SQLite dedup + TTL                       │  │
        │  └───────▲───────────────────────────▲───────────┘  │
        │          │ duplicate                  │ new          │
        │  ┌───────┴───────────────┐   ┌───────┴────────────┐  │
        │  │  5a) Link/Ignore      │   │  5b) Jira Publisher │  │
        │  │  (optional comment)   │   │  (REST API v3)      │  │
        │  └───────────────────────┘   └─────────────────────┘  │
        └─────────────────────────────────────────────────────┘
```

## Mermaid flow
```mermaid
flowchart TD
  A[Incoming Alert] --> B{Router}
  B -->|traffic| C[Traffic Agent + Tools]
  B -->|coupling| D[Coupling Agent + Tools]
  B -->|coatr| E[COATR Agent + Tools]
  C --> F[Findings + Evidence]
  D --> F
  E --> F
  F --> G[Conclusion Agent -> JSON]
  G --> H{Memory Dedup (SQLite)}
  H -->|Duplicate| I[Return link / optionally comment]
  H -->|New| J[Policy Check]
  J -->|Allowed| K[Create Jira Issue]
  J -->|Blocked| L[Return "no ticket"]
  K --> M[Upsert Incident Memory]
```
