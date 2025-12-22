def safe_md(text: str) -> str:
    # Minimal sanitizer to avoid breaking markup; expand if needed.
    return (text or "").replace("```", "''")
