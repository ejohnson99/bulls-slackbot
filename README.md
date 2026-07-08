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
  home game tomorrow (using Eastern time), and if so posts a message to
  Slack via an Incoming Webhook.
- `.github/workflows/daily.yml` runs both scripts once a day
  automatically, and also lets you trigger them manually.

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

- **Timing**: the workflow runs at 13:00 UTC (9 AM Eastern in summer,
  8 AM in winter). Edit the `cron` line in
  `.github/workflows/daily.yml` if you want a different time — cron
  times are always in UTC and don't auto-adjust for daylight saving.
- **Schedule changes**: the database is refreshed every day before the
  Slack check runs, so postponements/rescheduled games get picked up
  automatically.
- **Doubleheaders**: handled — if two home games land on the same date,
  you'll get a message for each, noting "Game 1"/"Game 2".
- **Testing**: you can run either script locally too:
  ```bash
  python scripts/build_schedule.py
  SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..." python scripts/notify_slack.py
  ```
- **No dependencies**: both scripts use only the Python standard
  library, so there's nothing to `pip install`.
