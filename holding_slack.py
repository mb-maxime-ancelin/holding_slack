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
from socket import timeout
import typer
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

app = typer.Typer()

SESSION_DIR = os.getenv("SESSION_DIR", ".session")
SLACK_URL = "https://app.slack.com/client"
HOLDED_URL = "https://app.holded.com/myzone"
HARVEST_URL = "https://marsbased.harvestapp.com/time"


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

        page.goto(SLACK_URL, wait_until="domcontentloaded")

        if action == "morning":
            # post morning
            page.get_by_label("Canales y mensajes directos").get_by_text("status").dblclick()
            page.get_by_role("paragraph").click()
            page.get_by_role("textbox", name="Mensaje a status").fill("morning")
            page.get_by_role("button", name="Enviar ahora").click()

            # start holded
            page.goto("https://app.holded.com/login?url_after_login=%2Fmyzone")
            page.get_by_role("button", name="Continue with Google").click()
            page.locator(".MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeLarge").click()

        elif action == "lunch":
            # post lunch
            page.get_by_label("Canales y mensajes directos").get_by_text("status").dblclick()
            page.get_by_role("paragraph").click()
            page.get_by_role("textbox", name="Mensaje a status").fill("lunch")
            page.get_by_role("button", name="Enviar ahora").click()

            # set status to eating
            page.get_by_role("button", name="Usuario: Maxime Ancelin").click()
            page.get_by_role("menuitem", name="Cómo actualizar tu estado").click()
            page.get_by_role("button", name="Estado 5 de 5, configurar").click()
            page.get_by_role("button", name="Guardar").click()

            # pause holded
            page.goto("https://app.holded.com/login?url_after_login=%2Fmyzone")
            page.get_by_role("button", name="Continue with Google").click()
            page.locator(".MuiStack-root.css-8v90jo > button:nth-child(2)").click()

        elif action == "back":
            # post back
            page.get_by_label("Canales y mensajes directos").get_by_text("status").dblclick()
            page.get_by_role("paragraph").click()
            page.get_by_role("textbox", name="Mensaje a status").fill("back")
            page.get_by_role("button", name="Enviar ahora").click()

            # restart holded
            page.goto("https://app.holded.com/login?url_after_login=%2Fmyzone")
            page.get_by_role("button", name="Continue with Google").click()
            page.locator(".MuiStack-root.css-8v90jo > span > .MuiButtonBase-root").click()

        elif action == "closing":
            # post closing
            page.get_by_label("Canales y mensajes directos").get_by_text("status").dblclick()
            page.get_by_role("paragraph").click()
            page.get_by_role("textbox", name="Mensaje a status").fill("closing")
            page.get_by_role("button", name="Enviar ahora").click()

            # stop holded
            page.goto("https://app.holded.com/login?url_after_login=%2Fmyzone")
            page.get_by_role("button", name="Continue with Google").click()
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

        elif action == "nothing":
            typer.echo(">>")

        typer.echo("Done")

        # page.pause()

        context.close()

# check flow
@app.command()
def nothing():
    typer.echo("nothing")
    run_browser("nothing")

@app.command()
def morning():
    typer.echo("morning")
    run_browser("morning")

@app.command()
def lunch():
    typer.echo("lunch")
    run_browser("lunch")

@app.command()
def back():
    typer.echo("back")
    run_browser("back")

@app.command()
def closing():
    typer.echo("closing")
    run_browser("closing")


if __name__ == "__main__":
    app()
