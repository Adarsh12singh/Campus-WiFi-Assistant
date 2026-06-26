import time
import threading

from core.network_manager import (
    connection_status,
    wait_for_stable_network
)
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
from core.recovery_manager import recover_connection
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

wait_for_stable_network()

print("Network Stable.")

last_login_attempt = 0
last_status = None
last_wifi = None

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

        connect_to_wifi(TARGET_WIFI)

        time.sleep(10)

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

        if current_time - last_login_attempt > 60:

            print("⚠ Login Required")

            show_notification(
                "📶 Campus WiFi Assistant",
                "🔄 Recovering Connection..."
            )

            recover_connection()
            set_state(RECOVERY)

            try:
                if smart_login():
                    write_log("Login Successful")
                    show_notification(
                        "📶 Campus WiFi Assistant",
                        "✅ Internet Connected"
                    )
                else:
                    write_log("All Login Attempts Failed")
                    show_notification(
                        "📶 Campus WiFi Assistant",
                        "❌ Unable To Login"
                    )
            except Exception as e:
                write_log(f"Login Failed: {e}")
                show_notification(
                    "📶 Campus WiFi Assistant",
                    "❌ Login Failed"
                )

            last_login_attempt = current_time

    elif status == "WIFI_DISCONNECTED":

        print("✗ WiFi Disconnected")

    time.sleep(15)