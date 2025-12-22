from crewai.tools import tool

@tool("run_sql")
def run_sql(query: str) -> dict:
    """Run SQL query (stub). Replace with real DB call."""
    return {"query": query, "rows": [], "rowcount": 0}
