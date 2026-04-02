#!/usr/bin/env python3
"""
Usage:
  ./script.py morning
  ./script.py closing

On first run, log in to Slack manually — the session is saved in SESSION_DIR
and reused on every subsequent run.

Dependencies:
  uv add playwright typer python-dotenv
  uv run playwright install chromium

.env file:
  SESSION_DIR=/home/<you>/.local/share/slack-bot/session
"""

import os
import typer
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

app = typer.Typer()

TARGET_URL   = "https://app.slack.com/client"
SESSION_DIR  = os.getenv("SESSION_DIR", ".session")


def run_browser(action: str):
    os.makedirs(SESSION_DIR, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            args=["--no-sandbox"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        typer.echo(f"Navigating to {TARGET_URL} ...")
        page.goto(TARGET_URL, wait_until="domcontentloaded")

        # If not logged in yet, wait longer for the user to log in manually
        page.wait_for_selector('[data-qa="channel_sidebar"]', timeout=120_000)
        typer.echo("Slack loaded!")

        # ── add your per-action automation steps below ────────────────────────
        if action == "morning":
            pass  # e.g. open standup channel, post a message, etc.
        elif action == "closing":
            pass  # e.g. set status to away, close channels, etc.
        # ──────────────────────────────────────────────────────────────────────

        page.pause()

        input("Press Enter to exit …")
        context.close()


@app.command()
def morning():
    """Start of day routine."""
    typer.echo("Hello!")
    run_browser("morning")


@app.command()
def closing():
    """End of day routine."""
    typer.echo("Bye!")
    run_browser("closing")


if __name__ == "__main__":
    app()
