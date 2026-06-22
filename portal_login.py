from playwright.sync_api import sync_playwright
import json


def login_to_portal():

    with open("config.json", "r") as f:
        config = json.load(f)

    username = config["username"]
    password = config["password"]
    portal_url = config["portal_url"]

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(portal_url)

        page.fill("#username", username)

        page.fill("#password", password)

        page.click("#loginbutton")

        page.wait_for_timeout(5000)

        browser.close()