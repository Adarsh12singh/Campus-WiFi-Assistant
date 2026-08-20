from core.profile_manager import get_profile_by_id
from core.credential_manager import get_credential
from core.strategies.playwright_strategy import PlaywrightStrategy
from core.strategies.base import LoginResult


def login_to_portal(profile=None, credentials=None):
    """
    Backward-compatible entry point for portal login.
    Uses PlaywrightStrategy with the specified profile or default 'ou_hostels'.
    """
    if profile is None:
        profile = get_profile_by_id("ou_hostels") or {
            "id": "ou_hostels",
            "name": "OU Hostels",
            "ssid": "OU Hostels",
            "portal_url": "http://172.16.1.1:8090/httpclient.html",
            "selectors": {
                "username": "#username",
                "password": "#password",
                "submit": "#loginbutton"
            },
            "data_limit_text": "data transfer has been exceeded",
            "credential_id": "ou_hostels_creds"
        }

    if credentials is None:
        cred_id = profile.get("credential_id", "ou_hostels_creds")
        credentials = get_credential(cred_id)

    strategy = PlaywrightStrategy()
    result = strategy.login(profile, credentials)

    if result == LoginResult.DATA_LIMIT:
        return "DATA_LIMIT"
    elif result == LoginResult.SUCCESS:
        return "SUCCESS"
    else:
        return "FAILED"