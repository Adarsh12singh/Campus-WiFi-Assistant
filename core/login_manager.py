import time
from core.network_manager import connection_status, get_active_network_profile
from core.profile_manager import find_profile_by_ssid, load_all_profiles
from core.credential_manager import get_credential
from core.strategies.factory import get_login_strategy
from core.strategies.base import LoginResult
from core.state_manager import (
    set_state,
    AUTHENTICATING,
    AUTHENTICATED,
    INTERNET_CONNECTED,
    DATA_LIMIT_EXCEEDED
)
from logger import write_log
from ui.notification_manager import show_notification
from utils.wifi_name import get_current_wifi


def smart_login(profile=None, max_attempts=None):
    """
    Attempts portal login using the appropriate profile and strategy,
    then verifies whether internet becomes available.
    """
    # 1. Resolve active profile
    if profile is None:
        profile = get_active_network_profile()

    if not profile:
        write_log("Smart Login Aborted: No matching network profile found for current WiFi")
        return "NO_PROFILE"

    profile_name = profile.get("name", "Unknown Network")
    attempts_limit = max_attempts or profile.get("retry_count", 3)
    retry_delay = profile.get("retry_delay_seconds", 10)
    strategy_name = profile.get("login_strategy", "playwright")

    # 2. Resolve credentials
    cred_id = profile.get("credential_id", "")
    creds = get_credential(cred_id)

    # 3. Instantiate strategy
    strategy = get_login_strategy(strategy_name)

    for attempt in range(1, attempts_limit + 1):
        print(f"========== [{profile_name}] LOGIN ATTEMPT {attempt}/{attempts_limit} ({strategy_name}) ==========")
        write_log(f"[{profile_name}] Login Attempt {attempt}/{attempts_limit}")

        set_state(AUTHENTICATING)
        show_notification(
            "📶 Campus WiFi Assistant",
            f"🔐 Logging into {profile_name}... Attempt {attempt}/{attempts_limit}"
        )

        try:
            result = strategy.login(profile, creds)

            if result == LoginResult.DATA_LIMIT:
                print(f"[{profile_name}] ⚠ DATA LIMIT EXCEEDED")
                write_log(f"[{profile_name}] Data Limit Exceeded")
                set_state(DATA_LIMIT_EXCEEDED)
                return "DATA_LIMIT"

            elif result == LoginResult.SUCCESS:
                print(f"[{profile_name}] Authentication submitted")
                set_state(AUTHENTICATED)

            else:
                print(f"[{profile_name}] Login execution returned {result.value}")
                write_log(f"[{profile_name}] Strategy returned {result.value}")

            # Give network/portal time to authenticate
            time.sleep(4)

            # Verification loop
            status = None
            for i in range(8):
                print(f"Checking Internet connection... {i+1}/8")
                status = connection_status(profile)
                if status == "CONNECTED":
                    break
                time.sleep(2)

            if status == "CONNECTED":
                print(f"[{profile_name}] ✓ LOGIN VERIFIED — Internet Connected")
                write_log(f"[{profile_name}] Internet Verified")
                set_state(INTERNET_CONNECTED)
                return "SUCCESS"

            print(f"[{profile_name}] Internet still not available after attempt {attempt}")
            write_log(f"[{profile_name}] Verification check failed")

        except Exception as e:
            print(f"[{profile_name}] Login Error: {e}")
            write_log(f"[{profile_name}] Login Error: {e}")

        time.sleep(retry_delay)

    print(f"[{profile_name}] ALL LOGIN ATTEMPTS FAILED")
    write_log(f"[{profile_name}] All Login Attempts Failed")

    show_notification(
        "📶 Campus WiFi Assistant",
        f"❌ Couldn't connect to {profile_name} automatically. You may log in manually."
    )

    return "FAILED"