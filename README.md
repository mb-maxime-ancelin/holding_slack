# holding_slack

Small Playwright automation that drives my daily ritual across three services:

- <img src="https://www.google.com/s2/favicons?domain=slack.com&sz=16" width="16" height="16" align="absmiddle" /> **Slack** — post a status message in `#status` and set the status emoji
- <img src="https://www.google.com/s2/favicons?domain=holded.com&sz=16" width="16" height="16" align="absmiddle" /> **Holded** — start / pause / resume / stop the time tracker
- <img src="https://www.google.com/s2/favicons?domain=harvestapp.com&sz=16" width="16" height="16" align="absmiddle" /> **Harvest** — copy yesterday's rows and set hours at end of day

## Commands

```bash
./holding_slack.py morning   # ☀️  post "morning"  + start Holded
./holding_slack.py lunch     # 🍔 post "lunch"    + set eating status + pause Holded
./holding_slack.py back      # 🌇 post "back"     + resume Holded
./holding_slack.py closing   # 🌙 post "closing"  + stop Holded + fill Harvest, give control back to user on Harvest for final confirmation
./holding_slack.py testing   # sanity-check the safe_go_to_holded flow
```

## Setup

```bash
uv sync
uv run playwright install chromium
cp .env.example .env   # then edit
```

On first run a Chromium window opens — log into Slack (and Holded via Google) manually. The session is persisted in `SESSION_DIR` and reused afterwards.

## `.env`

| key           | what it is                                                    |
| ------------- | ------------------------------------------------------------- |
| `SESSION_DIR` | Playwright persistent-context dir (browser profile + cookies) - `.session` by default|
| `SLACK_USER`        | Display name used in the Slack UI (`Usuario: <name>`)         |
