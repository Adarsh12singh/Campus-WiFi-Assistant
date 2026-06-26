from playwright.sync_api import sync_playwright

def login_to_portal():
    from core.config_manager import get_config

    config = get_config()

    username = config["username"]
    password = config["password"]
    portal_url = config["portal_url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            portal_url,
            wait_until="networkidle",
            timeout=30000
        )

        page.wait_for_selector(
            "#username",
            timeout=15000
        )

        page.fill("#username", username)
        page.fill("#password", password)
        page.click("#loginbutton")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        browser.close()
