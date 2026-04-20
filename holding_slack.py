#!/usr/bin/env -S uv run

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
import re
from socket import timeout
import typer
from rich import print
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

app = typer.Typer()

SESSION_DIR = os.getenv("SESSION_DIR", ".session")
SLACK_USER = os.getenv("SLACK_USER", "")
SLACK_URL = "https://app.slack.com/client"
HOLDED_URL = "https://app.holded.com/myzone"
HARVEST_URL = "https://marsbased.harvestapp.com/time"

SAFE_TIMEOUT = 5_000

def short_sleep(page):
    page.wait_for_timeout(SAFE_TIMEOUT)

def safe_go_to_slack(page):
    print(":slack:")
    try:
        page.goto(SLACK_URL, wait_until="domcontentloaded", timeout=SAFE_TIMEOUT)
    except:
        page.pause()
    # page.pause()

def set_status(page, status):
    page.get_by_label("Canales y mensajes directos").get_by_text("status").dblclick()
    page.get_by_role("paragraph").click()
    page.get_by_role("textbox", name="Mensaje a status").fill(status)
    page.get_by_role("button", name="Enviar ahora").click()


def safe_go_to_holded(page):
    print("holded:")
    try:
        # already logged in holded
        page.goto("https://app.holded.com/myzone", timeout=SAFE_TIMEOUT)
        page.pause()
        mb = page.get_by_role("button", name="MarsBased SL")
        mb.wait_for(state="visible", timeout=SAFE_TIMEOUT)
    except:
        # click login needed
        try:
            print("click login needed")
            page.goto("https://app.holded.com/login?url_after_login=%2Fmyzone")
            google_btn = page.get_by_role("button", name="Continue with Google")
            google_btn.wait_for(state="visible", timeout=SAFE_TIMEOUT)
            print("google_btn visible")
            google_btn.click(timeout=SAFE_TIMEOUT)
            print("click google btn")
            logo_button = page.get_by_role("navigation").get_by_role("link").filter(has_text=re.compile(r"^$"))
            logo_button.wait_for(state="visible", timeout=SAFE_TIMEOUT)
            print("-- click login needed : all ok")
        except:
            # auto login fails, manual login needed
            print("[bold red]holded: manual login required")
            page.pause()

def run_browser(action: str):
    os.makedirs(SESSION_DIR, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            no_viewport=True,
            args=["--no-sandbox"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        safe_go_to_slack(page)

        if action == "morning":
            # post morning
            set_status(page, "morning")

            # start holded
            safe_go_to_holded(page)
            page.locator(".MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeLarge").click()

        elif action == "lunch":
            # post lunch
            set_status(page, "lunch")

            # set status to eating
            page.get_by_role("button", name=f"Usuario: {SLACK_USER}").click()
            page.get_by_role("menuitem", name="Cómo actualizar tu estado").click()
            page.get_by_role("button", name="Estado 5 de 5, configurar").click()
            page.get_by_role("button", name="Guardar").click()

            # pause holded
            safe_go_to_holded(page)
            page.locator(".MuiStack-root.css-8v90jo > button:nth-child(2)").click()

        elif action == "back":
            # post back
            set_status(page, "back")

            # restart holded
            safe_go_to_holded(page)
            page.locator(".MuiStack-root.css-8v90jo > span > .MuiButtonBase-root").click()


        elif action == "closing":
            # post closing
            set_status(page, "closing")

            # stop holded
            safe_go_to_holded(page)
            page.locator(".MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeLarge").first.click()
            page.get_by_role("button", name="Sí, he terminado").click()

            # go to harvest
            page.goto("https://marsbased.harvestapp.com/time")
            page.get_by_role("button", name="Copy rows from most recent").click()
            page.get_by_role("button", name="Edit").click()
            page.get_by_role("textbox", name="hours").fill("8:00")

            # manual check before confirming
            typer.echo("confirm hours")
            page.pause()

        elif action == "testing":
            safe_go_to_holded(page)
            short_sleep(page)
            typer.echo(">>")

        typer.echo("Done")

        # page.pause()

        context.close()

# check flow
@app.command()
def testing():
    typer.echo("testing ...")
    run_browser("testing")

@app.command()
def morning():
    typer.echo("☀️ morning")
    run_browser("morning")

@app.command()
def lunch():
    typer.echo("🍔 lunch")
    run_browser("lunch")

@app.command()
def back():
    typer.echo("🌇 back")
    run_browser("back")

@app.command()
def closing():
    typer.echo("🌙 closing")
    run_browser("closing")


if __name__ == "__main__":
    app()
