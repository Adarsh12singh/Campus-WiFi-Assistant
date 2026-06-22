import pystray
from pystray import MenuItem as item
from PIL import Image
import os
import app_state


def create_image():
    """Load an icon image or create a simple fallback image."""
    try:
        return Image.open("campus_wifi.png")
    except Exception:
        img = Image.new("RGBA", (64, 64), (0, 122, 204, 255))
        return img


def pause_monitoring(icon, item):
    app_state.monitoring_enabled = False
    print("Monitoring Paused")


def resume_monitoring(icon, item):
    app_state.monitoring_enabled = True
    print("Monitoring Resumed")


def open_logs(icon, item):
    try:
        os.startfile("logs.txt")
    except Exception as e:
        print(f"Unable To Open Logs: {e}")


def open_config(icon, item):
    try:
        os.startfile("config.json")
    except Exception as e:
        print(f"Unable To Open Config: {e}")


def get_status(item):
    return f"Status: {app_state.current_status}"


def exit_app(icon, item):
    try:
        icon.stop()
    finally:
        os._exit(0)


def start_tray():
    menu = pystray.Menu(
        item(get_status, lambda icon, item: None, enabled=False),
        item("Pause Monitoring", pause_monitoring),
        item("Resume Monitoring", resume_monitoring),
        item("Open Logs", open_logs),
        item("Open Config", open_config),
        item("Exit", exit_app),
    )

    icon = pystray.Icon(
        "CampusWiFi",
        create_image(),
        "Campus WiFi Assistant",
        menu=menu,
    )

    icon.run()
