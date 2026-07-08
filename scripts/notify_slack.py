"""
Checks data/home_games.json for a Durham Bulls home game today
(America/New_York time) and, if one exists, posts a message to Slack
via an Incoming Webhook.

Requires the SLACK_WEBHOOK_URL environment variable.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
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


def main() -> None:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    games = load_games()

    today_eastern = datetime.now(EASTERN).date()
    today_str = today_eastern.strftime("%Y-%m-%d")

    todays_games = [g for g in games if g["date"] == today_str]

    if not todays_games:
        print(f"No Durham Bulls home game today ({today_str}). Nothing to post.")
        return

    pretty_date = today_eastern.strftime("%A, %B %-d")

    for game in todays_games:
        header = ":baseball: *Durham Bulls game today!*"
        dh_note = (
            f" (Game {game['game_number']} of a doubleheader)"
            if game.get("game_number", 1) > 1
            else ""
        )
        text = (
            f"{header}\n"
            f"{pretty_date} at *{game['time_display']}*{dh_note}\n"
            f"Durham Bulls vs *{game['opponent']}*\n"
            f"Durham Bulls Athletic Park"
        )
        post_to_slack(webhook_url, text)
        print(f"Posted to Slack: {game['date']} vs {game['opponent']}")


if __name__ == "__main__":
    main()
