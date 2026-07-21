import time
import threading
import os

from core.network_manager import (
    connection_status,
    wait_for_stable_network
)
from core.config_manager import CONFIG_PATH
from core.state_manager import (
    set_state,
    get_state,
    STARTING,
    WAITING_FOR_WIFI,
    VERIFYING_NETWORK,
    LOGIN_REQUIRED,
    CONNECTED,
    RECOVERY
)
from core.login_manager import smart_login
from logger import write_log
from utils.wifi_name import get_current_wifi
from utils.wifi_autoconnect import connect_to_wifi
from ui.notification_manager import show_notification
from ui.tray_app import start_tray
import app_state

print("Campus WiFi Assistant Started")
set_state(STARTING)

write_log("Application Started")

show_notification(
"📶 Campus WiFi Assistant",
"🚀 Monitoring Started"
)

tray_thread = threading.Thread(
target=start_tray,
daemon=True
)

tray_thread.start()

TARGET_WIFI = "OU Hostels"

print("Waiting for stable network...")

while True:

    current_wifi = get_current_wifi()

    if current_wifi == TARGET_WIFI:

        print("Network Stable.")

        break

    print("Waiting for OU Hostels WiFi...")

    connect_to_wifi(TARGET_WIFI)

    time.sleep(5)

last_login_attempt = 0
last_status = None
last_wifi = None

data_limit_active = False
data_limit_config_mtime = None
data_limit_first_seen = 0
DATA_LIMIT_FALLBACK_RETRY = 20 * 60  # retry anyway after 20 min, in case quota reset itself


def get_config_mtime():
    try:
        return os.path.getmtime(CONFIG_PATH)
    except OSError:
        return None

while True:

    if not app_state.monitoring_enabled:
        time.sleep(2)
        continue

    current_wifi = get_current_wifi()

    # Auto connect if no WiFi connected
    if not current_wifi:

        set_state(WAITING_FOR_WIFI)

        app_state.current_status = "No WiFi"

        print("No WiFi Connected")

        write_log("No WiFi Connected")

        if connect_to_wifi(TARGET_WIFI):
            write_log("Connection Requested")

        time.sleep(15)

        continue

    # WiFi changed
    if current_wifi != last_wifi:

        write_log(f"Connected WiFi: {current_wifi}")

        show_notification(
            "📶 Campus WiFi Assistant",
            f"📡 Connected to {current_wifi}"
        )

        last_wifi = current_wifi

    # Ignore non-hostel WiFi
    if current_wifi != TARGET_WIFI:

        app_state.current_status = f"Using {current_wifi}"

        print(f"Connected to {current_wifi} - Monitoring Disabled")

        time.sleep(15)

        continue

    status = connection_status()
    set_state(VERIFYING_NETWORK)

    if status != last_status:

        write_log(f"Status Changed: {status}")

        if status == "CONNECTED":
            set_state(CONNECTED)

            app_state.current_status = "Connected"
            print("STATUS =", app_state.current_status)

            show_notification(
                "📶 Campus WiFi Assistant",
                "✅ Internet Connected"
            )

        elif status == "WIFI_DISCONNECTED":

            app_state.current_status = "WiFi Disconnected"

            show_notification(
                "📶 Campus WiFi Assistant",
                "❌ WiFi Disconnected"
            )

        elif status == "CAPTIVE_PORTAL_OR_NO_INTERNET":
            set_state(LOGIN_REQUIRED)

            app_state.current_status = "Login Required"

            show_notification(
                "📶 Campus WiFi Assistant",
                "⚠ Login Required"
            )

        last_status = status

    if status == "CONNECTED":
        print("✓ Internet Connected")
    elif status == "CAPTIVE_PORTAL_OR_NO_INTERNET":
        current_time = time.time()

        if data_limit_active:

            current_mtime = get_config_mtime()

            config_updated = (
                current_mtime is not None
                and data_limit_config_mtime is not None
                and current_mtime != data_limit_config_mtime
            )

            timed_out = (current_time - data_limit_first_seen) > DATA_LIMIT_FALLBACK_RETRY

            if not config_updated and not timed_out:
                time.sleep(15)
                continue

            print("Retrying login (config changed or fallback timer reached)...")
            data_limit_active = False

        if current_time - last_login_attempt > 60:
            print("⚠ Portal Login Required")

            set_state(LOGIN_REQUIRED)

            show_notification(
                "📶 Campus WiFi Assistant",
                "🔐 Logging into Portal..."
            )

            try:
                result = smart_login()
                last_login_attempt = current_time

                if result == "SUCCESS":
                    print("✅ Login Successful")
                time.sleep(10)

                status = connection_status()

                if status == "CONNECTED":

                    print("Internet Verified")

                    set_state(CONNECTED)

                    app_state.current_status = "Connected"

                    write_log("Portal Login Successful")

                    show_notification(
                        "📶 Campus WiFi Assistant",
                        "✅ Internet Connected"
                    )

                    last_status = "CONNECTED"

                    continue

                elif result == "DATA_LIMIT":
                    print("⚠ Data Limit Exceeded")

                    write_log("Data Limit Exceeded")

                    show_notification(
                        "📶 Campus WiFi Assistant",
                        "📊 Daily Data Limit Exceeded — update your credentials to resume"
                    )

                    data_limit_active = True
                    data_limit_first_seen = current_time
                    data_limit_config_mtime = get_config_mtime()

                else:
                    print("❌ Login Failed")

                    write_log("Portal Login Failed")

                    show_notification(
                        "📶 Campus WiFi Assistant",
                        "❌ Login Failed"
                     )

            except Exception as e:
                print(e)
                write_log(f"Login Error: {e}")
                last_login_attempt = current_time

    elif status == "WIFI_DISCONNECTED":
        app_state.current_status = "WiFi Disconnected"

        show_notification(
            "📶 Campus WiFi Assistant",
            "❌ WiFi Disconnected"
        )

        print("✗ WiFi Disconnected")

    time.sleep(15)
