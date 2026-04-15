#!/usr/bin/env python3
"""Sleep Tracker AI — log sleep, analyse patterns, and get personalised recommendations. MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access
from persistence import ServerStore

import json
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

_store = ServerStore("sleep-tracker-ai")

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("sleep-tracker-ai", instructions="Track sleep duration and quality, analyse patterns, and get personalised sleep recommendations. By MEOK AI Labs.")


@mcp.tool()
def log_sleep(hours: float, quality: int = 5, bedtime: str = "", wake_time: str = "", notes: str = "", api_key: str = "") -> str:
    """Log a sleep entry. Hours slept, quality 1-10 (10=best), optional bedtime/wake_time (HH:MM), and notes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    hours = round(max(0, min(hours, 24)), 1)
    quality = max(1, min(quality, 10))
    entry = {
        "id": _store.list_length("sleep_logs") + 1,
        "hours": hours,
        "quality": quality,
        "bedtime": bedtime or None,
        "wake_time": wake_time or None,
        "notes": notes or None,
        "date": datetime.now(timezone.utc).date().isoformat(),
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    _store.append("sleep_logs", entry)
    # Quick feedback
    if hours < 6:
        feedback = "Below recommended sleep. Aim for 7-9 hours."
    elif hours > 9:
        feedback = "That's a lot of sleep. Oversleeping can also affect energy."
    elif quality >= 7:
        feedback = "Good sleep! Quality rest makes all the difference."
    elif quality <= 3:
        feedback = "Low quality. Consider your sleep environment and pre-bed routine."
    else:
        feedback = "Decent night. Small improvements in sleep hygiene can help."
    # Running averages
    all_logs = _store.list("sleep_logs")
    recent = all_logs[-7:] if len(all_logs) >= 7 else all_logs
    avg_hours = sum(e["hours"] for e in recent) / len(recent)
    avg_quality = sum(e["quality"] for e in recent) / len(recent)
    return json.dumps({
        "logged": entry,
        "feedback": feedback,
        "rolling_average": {
            "period": f"last {len(recent)} nights",
            "avg_hours": round(avg_hours, 1),
            "avg_quality": round(avg_quality, 1),
        },
        "total_entries": _store.list_length("sleep_logs"),
    }, indent=2)


@mcp.tool()
def get_sleep_stats(days: int = 7, api_key: str = "") -> str:
    """Get sleep statistics over the last N days. Includes averages, trends, and consistency scores."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    all_logs = _store.list("sleep_logs")
    if not all_logs:
        return json.dumps({"message": "No sleep data yet. Log your first night!", "entries": 0})
    days = max(1, min(days, 365))
    logs = all_logs[-days:] if len(all_logs) > days else all_logs
    hours_list = [e["hours"] for e in logs]
    quality_list = [e["quality"] for e in logs]
    avg_hours = sum(hours_list) / len(hours_list)
    avg_quality = sum(quality_list) / len(quality_list)
    # Consistency score (lower variance = higher consistency)
    if len(hours_list) >= 2:
        variance = sum((h - avg_hours) ** 2 for h in hours_list) / len(hours_list)
        consistency = max(0, round(100 - variance * 10, 1))  # rough 0-100 scale
    else:
        consistency = 100.0
    # Trend detection
    if len(hours_list) >= 4:
        first_half = sum(hours_list[:len(hours_list)//2]) / (len(hours_list)//2)
        second_half = sum(hours_list[len(hours_list)//2:]) / (len(hours_list) - len(hours_list)//2)
        if second_half > first_half + 0.3:
            trend = "improving"
        elif second_half < first_half - 0.3:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient data"
    # Sleep debt (based on 8h target)
    target = 8.0
    total_debt = sum(max(0, target - h) for h in hours_list)
    nights_below_target = sum(1 for h in hours_list if h < target)
    return json.dumps({
        "period": f"last {len(logs)} entries",
        "averages": {
            "hours": round(avg_hours, 1),
            "quality": round(avg_quality, 1),
        },
        "range": {
            "min_hours": min(hours_list),
            "max_hours": max(hours_list),
            "min_quality": min(quality_list),
            "max_quality": max(quality_list),
        },
        "consistency_score": consistency,
        "trend": trend,
        "sleep_debt": {
            "total_hours_below_target": round(total_debt, 1),
            "nights_below_8h": nights_below_target,
            "target_hours": target,
        },
        "entries": len(logs),
    }, indent=2)


@mcp.tool()
def analyze_patterns(api_key: str = "") -> str:
    """Analyse sleep patterns to find correlations between bedtime, duration, quality, and notes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    all_logs = _store.list("sleep_logs")
    if len(all_logs) < 3:
        return json.dumps({"message": f"Need at least 3 entries for pattern analysis. Currently have {len(all_logs)}."})
    # Duration vs quality correlation
    high_quality = [e for e in all_logs if e["quality"] >= 7]
    low_quality = [e for e in all_logs if e["quality"] <= 4]
    avg_hours_hq = sum(e["hours"] for e in high_quality) / len(high_quality) if high_quality else 0
    avg_hours_lq = sum(e["hours"] for e in low_quality) / len(low_quality) if low_quality else 0
    # Bedtime analysis
    bedtime_entries = [e for e in all_logs if e.get("bedtime")]
    bedtime_insight = None
    if bedtime_entries:
        early = [e for e in bedtime_entries if e["bedtime"] and e["bedtime"] < "23:00"]
        late = [e for e in bedtime_entries if e["bedtime"] and e["bedtime"] >= "23:00"]
        early_quality = sum(e["quality"] for e in early) / len(early) if early else 0
        late_quality = sum(e["quality"] for e in late) / len(late) if late else 0
        bedtime_insight = {
            "early_bed_avg_quality": round(early_quality, 1),
            "late_bed_avg_quality": round(late_quality, 1),
            "better_before_11pm": early_quality > late_quality if early and late else None,
        }
    # Weekly pattern
    best_night = max(all_logs, key=lambda e: e["quality"])
    worst_night = min(all_logs, key=lambda e: e["quality"])
    # Optimal range
    good_nights = [e for e in all_logs if e["quality"] >= 7]
    optimal_range = None
    if good_nights:
        optimal_min = min(e["hours"] for e in good_nights)
        optimal_max = max(e["hours"] for e in good_nights)
        optimal_range = {"min_hours": optimal_min, "max_hours": optimal_max}
    return json.dumps({
        "total_entries_analysed": len(all_logs),
        "duration_quality_link": {
            "high_quality_avg_hours": round(avg_hours_hq, 1) if high_quality else None,
            "low_quality_avg_hours": round(avg_hours_lq, 1) if low_quality else None,
            "insight": "Longer sleep correlates with better quality" if avg_hours_hq > avg_hours_lq else "Duration alone may not explain quality differences",
        },
        "bedtime_analysis": bedtime_insight,
        "optimal_sleep_range": optimal_range,
        "best_night": {"date": best_night["date"], "hours": best_night["hours"], "quality": best_night["quality"]},
        "worst_night": {"date": worst_night["date"], "hours": worst_night["hours"], "quality": worst_night["quality"]},
    }, indent=2)


@mcp.tool()
def get_recommendations(api_key: str = "") -> str:
    """Get personalised sleep improvement recommendations based on your logged data."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    recommendations = []
    priority_tips = []
    all_logs = _store.list("sleep_logs")
    if not all_logs:
        return json.dumps({
            "message": "Start logging sleep to get personalised recommendations!",
            "general_tips": [
                "Aim for 7-9 hours of sleep per night",
                "Keep a consistent bedtime and wake time",
                "Avoid screens 1 hour before bed",
                "Keep your bedroom cool, dark, and quiet",
                "Limit caffeine after 2pm",
            ],
        })
    recent = all_logs[-7:] if len(all_logs) >= 7 else all_logs
    avg_hours = sum(e["hours"] for e in recent) / len(recent)
    avg_quality = sum(e["quality"] for e in recent) / len(recent)
    # Duration recommendations
    if avg_hours < 6:
        priority_tips.append("URGENT: You are significantly sleep-deprived. Prioritise getting to bed earlier.")
        recommendations.append("Try moving your bedtime 30 minutes earlier each week until you reach 7+ hours.")
    elif avg_hours < 7:
        recommendations.append("You are slightly below the recommended 7-9 hours. Even 30 more minutes helps.")
    elif avg_hours > 9.5:
        recommendations.append("You may be oversleeping. Try setting a consistent alarm and getting up at the same time.")
    # Quality recommendations
    if avg_quality < 4:
        priority_tips.append("Sleep quality is very low. Review your sleep environment and habits.")
        recommendations.append("Evaluate: room temperature (18-20C ideal), noise, light, mattress comfort.")
        recommendations.append("Avoid alcohol and large meals within 3 hours of bedtime.")
    elif avg_quality < 6:
        recommendations.append("Quality could improve. Try a wind-down routine: reading, stretching, or meditation.")
    # Consistency
    hours_list = [e["hours"] for e in recent]
    if len(hours_list) >= 3:
        variance = sum((h - avg_hours) ** 2 for h in hours_list) / len(hours_list)
        if variance > 2:
            recommendations.append("Your sleep schedule is inconsistent. Aim for the same bedtime within 30 minutes daily.")
    # Bedtime analysis
    bedtime_entries = [e for e in recent if e.get("bedtime")]
    if bedtime_entries:
        late_nights = [e for e in bedtime_entries if e["bedtime"] and e["bedtime"] >= "00:00"]
        if len(late_nights) > len(bedtime_entries) * 0.5:
            recommendations.append("You often go to bed after midnight. Earlier bedtimes tend to improve sleep quality.")
    if not recommendations:
        recommendations.append("Your sleep looks healthy! Maintain your current routine.")
        recommendations.append("Consider tracking bedtime and wake time for deeper insights.")
    return json.dumps({
        "based_on": f"{len(recent)} recent entries",
        "current_averages": {
            "hours": round(avg_hours, 1),
            "quality": round(avg_quality, 1),
        },
        "priority_alerts": priority_tips if priority_tips else None,
        "recommendations": recommendations,
        "sleep_score": round(min(10, (avg_hours / 8 * 5) + (avg_quality / 10 * 5)), 1),
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
