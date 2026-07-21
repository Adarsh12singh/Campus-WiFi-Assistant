from playwright.sync_api import sync_playwright
from core.config_manager import get_config

config = get_config()

USERNAME = config["username"]
PASSWORD = config["password"]
URL = config["portal_url"]

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    page = browser.new_page()

    print("=" * 60)
    print("Opening Portal...")
    print("=" * 60)

    page.goto(URL)

    page.screenshot(path="step1_open.png")

    print("Current URL:", page.url)

    page.wait_for_selector("#username")

    print("Username Found")

    page.fill("#username", USERNAME)

    page.fill("#password", PASSWORD)

    page.screenshot(path="step2_filled.png")

    print("Credentials Filled")

    print("=" * 60)
    print("CLICKING LOGIN")
    print("=" * 60)

    page.click("#loginbutton")

    page.wait_for_timeout(8000)

    page.screenshot(path="step3_after_login.png")

    with open("after_login.html","w",encoding="utf8") as f:
        f.write(page.content())

    print("=" * 60)
    print("FINAL URL")
    print(page.url)
    print("=" * 60)

    print("TITLE:")
    print(page.title())

    print("=" * 60)

    input("Press ENTER to close browser...")

    browser.close()