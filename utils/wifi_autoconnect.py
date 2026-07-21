import subprocess
import time

from utils.wifi_name import get_current_wifi
from ui.notification_manager import show_notification


def connect_to_wifi(ssid):

    print(f"Trying to connect to {ssid}...")

    try:

        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "connect",
                f"name={ssid}"
            ],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print(result.stderr)

        # Wait for Windows to connect
        for _ in range(10):

            if get_current_wifi() == ssid:

                print("WiFi Connected Successfully")

                show_notification(
                    "📶 Campus WiFi Assistant",
                    f"📡 Connected to {ssid}"
                )

                return True

            time.sleep(2)

        print("WiFi Connection Timeout")

        show_notification(
            "📶 Campus WiFi Assistant",
            "❌ WiFi Connection Failed"
        )

        return False

    except Exception as e:

        print("WiFi Connect Error:", e)

        show_notification(
            "📶 Campus WiFi Assistant",
            "❌ Auto Connect Failed"
        )

        return False