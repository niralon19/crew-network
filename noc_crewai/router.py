from .models import Alert

def route_alert(alert: Alert) -> str:
    # Deterministic routing only
    if alert.type == "hermetic":
        return "traffic"
    if alert.type == "coupling":
        return "coupling"
    if alert.type == "coatr":
        return "coatr"
    raise ValueError(f"Unknown alert type: {alert.type}")
