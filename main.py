import time
import threading

from wifi_monitor import connection_status
from portal_login import login_to_portal
from logger import write_log
from utils.wifi_name import get_current_wifi
from utils.wifi_autoconnect import connect_to_wifi
from ui.notification_manager import show_notification
from ui.tray_app import start_tray
import app_state

print("Campus WiFi Assistant Started")

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

    if status != last_status:

        write_log(f"Status Changed: {status}")

        if status == "CONNECTED":

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

            write_log("Login Attempt Started")

            show_notification(
                "📶 Campus WiFi Assistant",
                "🔄 Reconnecting..."
            )

            try:

                time.sleep(10)

                login_to_portal()

                write_log("Login Attempt Completed")

                show_notification(
                    "📶 Campus WiFi Assistant",
                    "✅ Login Successful"
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