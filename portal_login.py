import traceback

from playwright.sync_api import sync_playwright
from logger import write_log


def login_to_portal():

    write_log("===== LOGIN FUNCTION STARTED =====")

    from core.config_manager import get_config

    config = get_config()

    username = config["username"]
    password = config["password"]
    portal_url = config["portal_url"]

    write_log(f"Portal URL: {portal_url}")

    with sync_playwright() as p:

        write_log("Launching Browser...")

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        try:

            write_log("Opening Portal...")

            page.goto(
                portal_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            write_log("Portal Opened")

            write_log("Waiting For Username Field...")

            page.wait_for_selector(
                "#username",
                timeout=10000
            )

            write_log("Username Field Found")

            page.fill("#username", username)
            write_log("Username Filled")

            page.fill("#password", password)
            write_log("Password Filled")

            write_log("Clicking Login Button...")

            page.click("#loginbutton")

            write_log("Login Button Clicked")

            write_log("Waiting for portal to process login...")

            page.wait_for_timeout(8000)

            html = page.content().lower()

            if "data transfer has been exceeded" in html:
                write_log("DATA LIMIT DETECTED")
                return "DATA_LIMIT"

            # We don't decide success/failure here anymore.
            # login_manager.py will verify internet availability.

            write_log("LOGIN REQUEST SENT")

            return "SUCCESS"

        except Exception as e:

            write_log(f"PORTAL LOGIN ERROR: {e}")
            write_log(f"PORTAL LOGIN TRACEBACK: {traceback.format_exc()}")

            return "FAILED"

        finally:

            write_log("Closing Browser...")

            browser.close()

            write_log("Browser Closed")