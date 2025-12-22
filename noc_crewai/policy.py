from .models import Conclusion

def should_open_jira(conclusion: Conclusion) -> bool:
    # Conservative defaults
    if conclusion.confidence == "low":
        return False
    priority = (conclusion.ownership or {}).get("priority", "P2")
    if priority not in ("P0", "P1"):
        return False
    return bool(conclusion.requires_human_approval)
