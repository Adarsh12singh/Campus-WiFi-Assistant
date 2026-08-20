import time
import threading
import os
import sys

# MUST be set before any module below imports playwright.
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
)

import app_state
from app_paths import get_app_dir
from logger import write_log
from core.state_manager import (
    set_state,
    get_state,
    STARTING,
    DISCONNECTED,
    WIFI_CONNECTING,
    WIFI_CONNECTED,
    CHECKING_INTERNET,
    CAPTIVE_PORTAL,
    AUTHENTICATING,
    AUTHENTICATED,
    INTERNET_CONNECTED,
    DATA_LIMIT_EXCEEDED,
    UNKNOWN_NETWORK
)
from core.config_manager import get_config, CONFIG_PATH
from core.profile_manager import find_profile_by_ssid, load_all_profiles
from core.credential_manager import CREDENTIALS_FILE
from core.network_manager import connection_status, get_active_network_profile
from core.login_manager import smart_login
from utils.wifi_name import get_current_wifi
from utils.wifi_autoconnect import connect_to_wifi
from ui.notification_manager import show_notification
from ui.tray_app import start_tray


def get_file_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def network_monitor_loop():
    """Background monitoring loop running on a dedicated worker thread."""
    last_login_attempt = 0
    last_status = None
    last_wifi = None

    data_limit_active = False
    data_limit_creds_mtime = None
    data_limit_first_seen = 0
    DATA_LIMIT_FALLBACK_RETRY = 20 * 60

    while True:
        try:
            config = get_config()
            interval = config.get("check_interval_seconds", 15)

            if not app_state.monitoring_enabled:
                app_state.current_status = "Monitoring Paused"
                time.sleep(2)
                continue

            current_wifi = get_current_wifi()
            app_state.current_ssid = current_wifi

            # 1. No WiFi connected
            if not current_wifi:
                set_state(DISCONNECTED)
                app_state.current_status = "No WiFi"
                app_state.current_profile_name = None

                if last_status != "WIFI_DISCONNECTED":
                    write_log("No WiFi Connected")
                    last_status = "WIFI_DISCONNECTED"

                if config.get("wifi_autoconnect_enabled", True):
                    pref_target = config.get("preferred_target_wifi", "OU Hostels")
                    set_state(WIFI_CONNECTING)
                    if connect_to_wifi(pref_target):
                        write_log(f"Auto-connected to {pref_target}")

                time.sleep(interval)
                continue

            # 2. WiFi changed notification
            if current_wifi != last_wifi:
                write_log(f"Connected WiFi: {current_wifi}")
                show_notification(
                    "📶 Campus WiFi Assistant",
                    f"📡 Connected to {current_wifi}"
                )
                last_wifi = current_wifi

            # 3. Lookup matching Network Profile
            active_profile = find_profile_by_ssid(current_wifi)

            if not active_profile:
                app_state.current_profile_name = None
                app_state.current_status = f"Using {current_wifi} (Unmanaged)"
                set_state(UNKNOWN_NETWORK)
                time.sleep(interval)
                continue

            # Known managed profile
            app_state.current_profile_name = active_profile.get("name", current_wifi)
            status = connection_status(active_profile)

            if status != last_status:
                write_log(f"[{active_profile.get('name')}] Status Changed: {status}")

                if status == "CONNECTED":
                    set_state(INTERNET_CONNECTED)
                    app_state.current_status = "Connected"
                    show_notification(
                        "📶 Campus WiFi Assistant",
                        f"✅ Internet Connected ({active_profile.get('name')})"
                    )

                elif status == "CAPTIVE_PORTAL_OR_NO_INTERNET":
                    set_state(CAPTIVE_PORTAL)
                    app_state.current_status = "Login Required"
                    show_notification(
                        "📶 Campus WiFi Assistant",
                        f"⚠ Login Required ({active_profile.get('name')})"
                    )

                last_status = status

            # 4. Handle Captive Portal Login
            if status == "CAPTIVE_PORTAL_OR_NO_INTERNET":
                current_time = time.time()

                if data_limit_active:
                    current_creds_mtime = get_file_mtime(CREDENTIALS_FILE)
                    creds_updated = (
                        current_creds_mtime is not None
                        and data_limit_creds_mtime is not None
                        and current_creds_mtime != data_limit_creds_mtime
                    )
                    timed_out = (current_time - data_limit_first_seen) > DATA_LIMIT_FALLBACK_RETRY

                    if not creds_updated and not timed_out:
                        time.sleep(interval)
                        continue

                    print(f"[{active_profile.get('name')}] Retrying login (credentials updated or fallback timer elapsed)...")
                    data_limit_active = False

                if current_time - last_login_attempt > 45:
                    print(f"[{active_profile.get('name')}] Initiating automated portal authentication...")
                    result = smart_login(active_profile)
                    last_login_attempt = current_time

                    if result == "SUCCESS":
                        app_state.current_status = "Connected"
                        last_status = "CONNECTED"
                        data_limit_active = False

                    elif result == "DATA_LIMIT":
                        app_state.current_status = "Data Limit Exceeded"
                        data_limit_active = True
                        data_limit_first_seen = current_time
                        data_limit_creds_mtime = get_file_mtime(CREDENTIALS_FILE)

                        show_notification(
                            "📶 Campus WiFi Assistant",
                            f"📊 Data Limit Exceeded on {active_profile.get('name')} — update credentials to resume"
                        )

                    else:
                        app_state.current_status = "Login Failed"

            elif status == "CONNECTED":
                app_state.current_status = "Connected"
                set_state(INTERNET_CONNECTED)

            time.sleep(interval)

        except Exception as e:
            print(f"Monitor loop error: {e}")
            write_log(f"Monitor Loop Error: {e}")
            time.sleep(10)


def main():
    print("==================================================")
    print("      Campus WiFi Assistant (V3 Multi-Network)    ")
    print("==================================================")
    set_state(STARTING)
    write_log("Campus WiFi Assistant V3 Started")

    show_notification(
        "📶 Campus WiFi Assistant",
        "🚀 Monitoring Started (V3 Multi-Network)"
    )

    # Start Background Network Monitor thread
    monitor_thread = threading.Thread(target=network_monitor_loop, daemon=True)
    monitor_thread.start()

    # Main thread runs the System Tray GUI Message Pump
    start_tray()


if __name__ == "__main__":
    main()
