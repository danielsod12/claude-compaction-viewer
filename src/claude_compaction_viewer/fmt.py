"""Formatting helpers for timestamps, tokens, and display."""

from datetime import datetime


def format_timestamp(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ts[:19]


def format_timestamp_full(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return ts


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def format_duration(first_ts: str, last_ts: str) -> str:
    if not first_ts or not last_ts:
        return ""
    try:
        t1 = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        mins = (t2 - t1).total_seconds() / 60
        if mins > 60:
            return f"{mins/60:.1f}h"
        return f"{mins:.0f}min"
    except (ValueError, TypeError):
        return ""
