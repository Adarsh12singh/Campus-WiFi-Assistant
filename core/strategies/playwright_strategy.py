from playwright.sync_api import sync_playwright
from core.strategies.base import BaseLoginStrategy, LoginResult
from logger import write_log


class PlaywrightStrategy(BaseLoginStrategy):
    """
    Playwright-based browser automation strategy.
    Preserves existing robust login flow for OU Hostels and JavaScript-heavy portals.
    """

    def __init__(self):
        super().__init__(name="playwright")

    def login(self, profile: dict, credentials: dict) -> LoginResult:
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        portal_url = profile.get("portal_url", "")
        selectors = profile.get("selectors", {})

        user_selector = selectors.get("username", "#username")
        pass_selector = selectors.get("password", "#password")
        submit_selector = selectors.get("submit", "#loginbutton")
        data_limit_text = profile.get("data_limit_text", "data transfer has been exceeded").lower()

        if not username or not password or not portal_url:
            write_log(f"PlaywrightStrategy Error: Missing credentials or portal URL for profile {profile.get('name')}")
            return LoginResult.FAILED

        print(f"[{profile.get('name')}] Launching Browser (Playwright Strategy)...")
        write_log(f"[{profile.get('name')}] Starting Playwright authentication")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                try:
                    print(f"[{profile.get('name')}] Navigating to {portal_url}...")
                    page.goto(
                        portal_url,
                        wait_until="domcontentloaded",
                        timeout=30000
                    )

                    print(f"[{profile.get('name')}] Waiting for username field ({user_selector})...")
                    page.wait_for_selector(user_selector, timeout=10000)

                    page.fill(user_selector, username)
                    page.fill(pass_selector, password)

                    print(f"[{profile.get('name')}] Submitting login ({submit_selector})...")
                    page.click(submit_selector)

                    print(f"[{profile.get('name')}] Waiting for portal processing...")
                    page.wait_for_timeout(8000)

                    html = page.content().lower()

                    if data_limit_text and data_limit_text in html:
                        print(f"[{profile.get('name')}] DATA LIMIT DETECTED")
                        write_log(f"[{profile.get('name')}] Quota limit detected")
                        return LoginResult.DATA_LIMIT

                    print(f"[{profile.get('name')}] Login request submitted")
                    return LoginResult.SUCCESS

                finally:
                    browser.close()

        except Exception as e:
            print(f"[{profile.get('name')}] Playwright Login Error: {e}")
            write_log(f"[{profile.get('name')}] Playwright Login Error: {e}")
            return LoginResult.ERROR
