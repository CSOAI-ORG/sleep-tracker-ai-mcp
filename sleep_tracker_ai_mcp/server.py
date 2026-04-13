from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sleep-tracker")

SLEEP_LOG = []

@mcp.tool()
def log_sleep(date: str, hours: float, quality: int = 5) -> dict:
    """Log a sleep entry. Quality is 1-10."""
    entry = {"date": date, "hours": hours, "quality": max(1, min(10, quality))}
    SLEEP_LOG.append(entry)
    return {"logged": entry, "total_entries": len(SLEEP_LOG)}

@mcp.tool()
def calculate_sleep_debt(target_hours: float = 8.0) -> dict:
    """Calculate total sleep debt."""
    if not SLEEP_LOG:
        return {"sleep_debt": 0.0, "entries": 0}
    total_target = target_hours * len(SLEEP_LOG)
    total_slept = sum(e["hours"] for e in SLEEP_LOG)
    debt = max(0.0, total_target - total_slept)
    return {"sleep_debt_hours": round(debt, 2), "average_hours": round(total_slept / len(SLEEP_LOG), 2), "entries": len(SLEEP_LOG)}

@mcp.tool()
def get_sleep_trends(last_n: int = 7) -> dict:
    """Get sleep trends for the last N entries."""
    recent = SLEEP_LOG[-last_n:]
    if not recent:
        return {"error": "No sleep data"}
    avg_hours = sum(e["hours"] for e in recent) / len(recent)
    avg_quality = sum(e["quality"] for e in recent) / len(recent)
    return {
        "entries_considered": len(recent),
        "average_hours": round(avg_hours, 2),
        "average_quality": round(avg_quality, 1),
        "consistency_score": round(100 - min(abs(avg_hours - 8) * 10, 100), 1),
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
