import requests
from core.strategies.base import BaseLoginStrategy, LoginResult
from logger import write_log


class HttpStrategy(BaseLoginStrategy):
    """
    Lightweight HTTP POST / GET form authentication strategy.
    Fast execution for standard form-based campus portals without launching a browser.
    """

    def __init__(self):
        super().__init__(name="http_post")

    def login(self, profile: dict, credentials: dict) -> LoginResult:
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        portal_url = profile.get("portal_url", "")
        post_config = profile.get("post_data", {})
        data_limit_text = profile.get("data_limit_text", "quota exceeded").lower()

        if not username or not password or not portal_url:
            write_log(f"HttpStrategy Error: Missing credentials or portal URL for {profile.get('name')}")
            return LoginResult.FAILED

        user_field = post_config.get("user_field", "username")
        pass_field = post_config.get("pass_field", "password")
        extra_fields = post_config.get("extra_fields", {})

        payload = {
            user_field: username,
            pass_field: password,
            **extra_fields
        }

        write_log(f"[{profile.get('name')}] Submitting HTTP POST authentication")

        try:
            session = requests.Session()
            response = session.post(
                portal_url,
                data=payload,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )

            body = response.text.lower()
            if data_limit_text and data_limit_text in body:
                write_log(f"[{profile.get('name')}] HTTP Strategy detected quota limit")
                return LoginResult.DATA_LIMIT

            if response.status_code in [200, 302]:
                return LoginResult.SUCCESS

            return LoginResult.FAILED

        except Exception as e:
            write_log(f"[{profile.get('name')}] HTTP Strategy Error: {e}")
            return LoginResult.ERROR
