from crewai.tools import tool

@tool("check_traffic")
def check_traffic(service: str, window_minutes: int = 10) -> dict:
    """Check traffic integrity for a service (stub).
    Replace with real implementation that queries Prometheus/Grafana/etc.
    """
    return {"service": service, "window_minutes": window_minutes, "traffic_delta_pct": 0.0, "status": "ok"}
