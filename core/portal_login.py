from playwright.sync_api import sync_playwright


def login_to_portal():

    print("===== LOGIN FUNCTION STARTED =====")

    from core.config_manager import get_config

    config = get_config()

    username = config["username"]
    password = config["password"]
    portal_url = config["portal_url"]

    print("Portal URL:", portal_url)

    with sync_playwright() as p:

        print("Launching Browser...")

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        try:

            print("Opening Portal...")

            page.goto(
                portal_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            print("Portal Opened")

            print("Waiting For Username Field...")

            page.wait_for_selector(
                "#username",
                timeout=10000
            )

            print("Username Field Found")

            page.fill("#username", username)
            print("Username Filled")

            page.fill("#password", password)
            print("Password Filled")

            print("Clicking Login Button...")

            page.click("#loginbutton")

            print("Login Button Clicked")

            print("Waiting for portal to process login...")

            page.wait_for_timeout(8000)

            html = page.content().lower()

            if "data transfer has been exceeded" in html:
                print("DATA LIMIT DETECTED")
                return "DATA_LIMIT"

            # We don't decide success/failure here anymore.
            # login_manager.py will verify internet availability.

            print("LOGIN REQUEST SENT")

            return "SUCCESS"

        except Exception as e:

            print("PORTAL LOGIN ERROR:", e)

            return "FAILED"

        finally:

            print("Closing Browser...")

            browser.close()

            print("Browser Closed")