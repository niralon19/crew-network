from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

AlertType = Literal["hermetic", "coupling", "coatr"]
Severity = Literal["info", "warning", "critical"]

class Alert(BaseModel):
    id: str = Field(..., description="Unique alert id from source (Grafana/Prometheus)")
    type: AlertType
    service: str
    description: str
    severity: Severity
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Finding(BaseModel):
    agent: str
    finding: str
    confidence: Literal["low", "medium", "high"] = "medium"

class Evidence(BaseModel):
    logs: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    sql: Dict[str, Any] = Field(default_factory=dict)

class Conclusion(BaseModel):
    summary: str
    root_cause: str
    why_it_happened: List[str]
    actions: Dict[str, List[str]]  # immediate/short_term/long_term
    ownership: Dict[str, str]      # team, priority
    confidence: Literal["low", "medium", "high"]
    requires_human_approval: bool = True
