from crewai.tools import tool

@tool("analyze_logs")
def analyze_logs(service: str, window_minutes: int = 10) -> dict:
    """Analyze logs (stub)."""
    return {"service": service, "window_minutes": window_minutes, "signals": [], "errors": []}
