import subprocess
from ui.notification_manager import show_notification

def connect_to_wifi(ssid):

    try:

        subprocess.run(
            f'netsh wlan connect name="{ssid}"',
            shell=True,
            capture_output=True
        )

        show_notification(
            "📶 Campus WiFi Assistant",
            f"📡 Connected to {ssid}"
        )

        return True

    except Exception as e:

        print("WiFi Connect Error:", e)

        show_notification(
            "📶 Campus WiFi Assistant",
            "❌ Auto Connect Failed"
        )

        return False