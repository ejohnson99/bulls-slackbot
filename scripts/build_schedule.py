"""
Builds/refreshes data/home_games.json — the "database" of Durham Bulls
home games (opponent, date, time) — by pulling the season schedule from
the free, public MLB Stats API.

Durham Bulls are Triple-A (sportId=11), teamId=234.

Usage:
    python scripts/build_schedule.py            # current year
    python scripts/build_schedule.py 2027       # specific season
"""

import json
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

TEAM_ID = 234
SPORT_ID = 11
EASTERN = ZoneInfo("America/New_York")
OUTPUT_PATH = "data/home_games.json"


def fetch_schedule(season: str) -> dict:
    url = (
        "https://statsapi.mlb.com/api/v1/schedule"
        f"?sportId={SPORT_ID}&teamId={TEAM_ID}&season={season}"
        "&gameType=R"  # regular season games
    )
    req = urllib.request.Request(url, headers={"User-Agent": "durham-bulls-slack-bot"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def extract_home_games(schedule_data: dict) -> list[dict]:
    games = []
    for date_entry in schedule_data.get("dates", []):
        for g in date_entry.get("games", []):
            home_team = g["teams"]["home"]["team"]
            if home_team["id"] != TEAM_ID:
                continue  # skip away games

            away_team_name = g["teams"]["away"]["team"]["name"]
            game_utc = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
            game_eastern = game_utc.astimezone(EASTERN)

            games.append(
                {
                    "game_pk": g["gamePk"],
                    "date": game_eastern.strftime("%Y-%m-%d"),
                    "time": game_eastern.strftime("%H:%M"),
                    "time_display": game_eastern.strftime("%-I:%M %p ET"),
                    "opponent": away_team_name,
                    "status": g.get("status", {}).get("detailedState", ""),
                    "game_number": g.get("gameNumber", 1),  # >1 means doubleheader
                }
            )

    games.sort(key=lambda x: (x["date"], x["time"], x["game_number"]))
    return games


def main() -> None:
    season = sys.argv[1] if len(sys.argv) > 1 else str(datetime.now(EASTERN).year)
    schedule_data = fetch_schedule(season)
    games = extract_home_games(schedule_data)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(games, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(games)} home games for {season} season to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
