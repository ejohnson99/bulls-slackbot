# Durham Bulls Slack Notifier

Posts in a Slack channel the day before every Durham Bulls **home** game,
with the opponent, date, and time. Runs entirely on GitHub Actions —
no server required.

## How it works

- `scripts/build_schedule.py` pulls the season schedule from the free,
  public [MLB Stats API](https://statsapi.mlb.com/) (Durham Bulls =
  Triple-A, team ID 234) and writes the home games to
  `data/home_games.json`. This is the "database."
- `scripts/notify_slack.py` reads that file, checks whether there's a
  home game today (using Eastern time), and if so posts a message to
  Slack via an Incoming Webhook.
- `scripts/weekly_digest.py` reads the database and posts a summary of
  all home games for the current week (Sunday–Saturday), or "No home
  games this week" if there are none.
- `.github/workflows/daily.yml` runs the daily check once a day.
- `.github/workflows/weekly.yml` runs the weekly digest every Sunday
  at noon Eastern.

Both workflows also refresh `data/home_games.json` before checking, so
postponements/rescheduled games get picked up automatically no matter
which one runs first.

## Setup

### 1. Create the repo
Create a new GitHub repo and add all the files in this project to it
(keep the folder structure — `.github/workflows/`, `scripts/`, `data/`).

### 2. Create a Slack Incoming Webhook
1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**.
2. Name it (e.g. "Durham Bulls Bot") and pick your workspace.
3. In the app settings, open **Incoming Webhooks** and switch it **On**.
4. Click **Add New Webhook to Workspace**, choose the public channel you
   want game announcements in, and authorize it.
5. Copy the webhook URL (looks like `https://hooks.slack.com/services/...`).

### 3. Add the webhook URL as a repo secret
In your GitHub repo: **Settings → Secrets and variables → Actions →
New repository secret**
- Name: `SLACK_WEBHOOK_URL`
- Value: the webhook URL from step 2

### 4. Run it once manually
Go to the **Actions** tab → **Durham Bulls Game Notifier** → **Run
workflow**. This builds `data/home_games.json` for the first time and
sends a test post if there happens to be a home game tomorrow.

After that, it runs automatically every day.

## Notes & things you may want to tweak

- **Timing**: the daily workflow runs at 13:00 UTC (9 AM Eastern in
  summer, 8 AM in winter); the weekly digest runs Sundays at 16:00 UTC
  (noon Eastern in summer, 11 AM in winter). Edit the `cron` lines in
  the respective workflow files if you want different times — cron
  times are always in UTC and don't auto-adjust for daylight saving.
- **Schedule changes**: the database is refreshed every time either
  workflow runs, so postponements/rescheduled games get picked up
  automatically.
- **Doubleheaders**: handled in both the daily and weekly messages —
  each game gets its own line/post, noting "Game 1"/"Game 2" where
  relevant.
- **Testing**: you can run any of the scripts locally too:
  ```bash
  python scripts/build_schedule.py
  SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..." python scripts/notify_slack.py
  SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..." python scripts/weekly_digest.py
  ```
- **No dependencies**: all scripts use only the Python standard
  library, so there's nothing to `pip install`.
