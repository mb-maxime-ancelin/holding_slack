#!/usr/bin/env python3

"""
Usage:
  python script.py morning
  python script.py closing

Dependencies:
  pip install playwright typer python-dotenv
  playwright install firefox

.env file:
  PATH_PROFILE=/home/<you>/snap/firefox/common/.mozilla/firefox/<your-profile>
"""

import subprocess
import time
import typer
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os

load_dotenv()

app = typer.Typer()

DEBUGGING_URL = "http://localhost:9222"
SLACK_URL    = "https://app.slack.com/client"


def launch_firefox():
    profile = os.getenv("PATH_PROFILE")
    if not profile:
        typer.echo("ERROR: PATH_PROFILE not set in .env", err=True)
        raise typer.Exit(1)

    typer.echo(f"Launching Firefox with profile: {profile}")
    subprocess.Popen([
        "firefox",
        "--start-debugger-server", "9222",
        "--profile", profile,
    ])
    time.sleep(3)  # give Firefox time to start


def run_browser(action: str):
    with sync_playwright() as p:
        browser = p.firefox.connect_over_cdp(DEBUGGING_URL)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        typer.echo(f"Navigating to {SLACK_URL} ...")
        page.goto(SLACK_URL, wait_until="domcontentloaded")
        page.wait_for_selector('[data-qa="channel_sidebar"]', timeout=30_000)
        typer.echo("Slack loaded!")

        # ── add your per-action automation steps below ────────────────────────
        if action == "morning":
            pass  # e.g. open standup channel, post a message, etc.
        elif action == "closing":
            pass  # e.g. set status to away, close channels, etc.
        # ──────────────────────────────────────────────────────────────────────

        page.pause()

        input("Press Enter to exit …")
        browser.close()


@app.command()
def morning():
    """Start of day routine."""
    typer.echo("Hello!")
    launch_firefox()
    run_browser("morning")


@app.command()
def closing():
    """End of day routine."""
    typer.echo("Bye!")
    launch_firefox()
    run_browser("closing")


if __name__ == "__main__":
    app()
