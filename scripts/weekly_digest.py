"""
Posts a weekly digest of Durham Bulls home games to Slack.

Looks at the current week — Sunday through Saturday, America/New_York
time — and either lists each home game or reports that there are none.

Requires the SLACK_WEBHOOK_URL environment variable.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DB_PATH = "data/home_games.json"
EASTERN = ZoneInfo("America/New_York")


def load_games() -> list[dict]:
    with open(DB_PATH) as f:
        return json.load(f)


def post_to_slack(webhook_url: str, text: str) -> None:
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        if body != "ok":
            print(f"Unexpected Slack response: {resp.status} {body}", file=sys.stderr)


def week_bounds(today):
    """Return (sunday, saturday) dates for the week containing `today`,
    with weeks starting on Sunday."""
    # Python's date.weekday(): Monday=0 ... Sunday=6
    days_since_sunday = (today.weekday() + 1) % 7
    sunday = today - timedelta(days=days_since_sunday)
    saturday = sunday + timedelta(days=6)
    return sunday, saturday


def format_game_line(game: dict) -> str:
    dt = datetime.strptime(f"{game['date']} {game['time']}", "%Y-%m-%d %H:%M")
    weekday = dt.strftime("%A")
    date_part =
