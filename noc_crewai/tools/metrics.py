from crewai.tools import tool

@tool("check_ratios")
def check_ratios(service: str, window_minutes: int = 10) -> dict:
    """Check coupling/ratios KPIs (stub)."""
    return {"service": service, "window_minutes": window_minutes, "ratio_ok": True, "details": {}}
