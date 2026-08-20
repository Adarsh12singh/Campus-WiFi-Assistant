import pystray
from pystray import MenuItem as item
from PIL import Image
import os
import threading
import app_state

from app_paths import get_app_dir, get_resource_dir
from ui.switch_account import open_switch_account_window
from ui.dashboard import open_dashboard
from startup_manager import add_to_startup, remove_from_startup, is_in_startup


def create_image():
    """Load an icon image or create a simple fallback image."""
    try:
        return Image.open(os.path.join(get_resource_dir(), "campus_wifi.png"))
    except Exception:
        img = Image.new("RGBA", (64, 64), (0, 122, 204, 255))
        return img


def pause_monitoring(icon, item):
    app_state.monitoring_enabled = False
    print("Monitoring Paused")


def resume_monitoring(icon, item):
    app_state.monitoring_enabled = True
    print("Monitoring Resumed")


def open_dashboard_window(icon, item):
    threading.Thread(target=open_dashboard, daemon=True).start()


def open_logs(icon, item):
    try:
        os.startfile(os.path.join(get_app_dir(), "logs.txt"))
    except Exception as e:
        print(f"Unable To Open Logs: {e}")


def switch_account(icon, item):
    try:
        threading.Thread(target=open_switch_account_window, daemon=True).start()
    except Exception as e:
        print(f"Unable To Open Switch Account Window: {e}")


def toggle_startup(icon, item):
    try:
        if is_in_startup():
            remove_from_startup()
        else:
            add_to_startup()
    except Exception as e:
        print(f"Unable To Update Startup Setting: {e}")


def startup_checked(item):
    try:
        return is_in_startup()
    except Exception:
        return False


def get_status(item):
    prof_text = f" ({app_state.current_profile_name})" if app_state.current_profile_name else ""
    return f"Status: {app_state.current_status}{prof_text}"


def exit_app(icon, item):
    try:
        icon.stop()
    finally:
        os._exit(0)


def start_tray():
    from ui.icon_holder import set_global_icon

    menu = pystray.Menu(
        item(get_status, lambda icon, item: None, enabled=False),
        item("📊 Open Dashboard", open_dashboard_window),
        item("🔑 Switch Account / Credentials", switch_account),
        item("⏸ Pause Monitoring", pause_monitoring, visible=lambda item: app_state.monitoring_enabled),
        item("▶ Resume Monitoring", resume_monitoring, visible=lambda item: not app_state.monitoring_enabled),
        item("Start with Windows", toggle_startup, checked=startup_checked),
        item("📜 Open Logs", open_logs),
        item("❌ Exit", exit_app),
    )

    icon = pystray.Icon(
        "CampusWiFi",
        create_image(),
        "Campus WiFi Assistant",
        menu=menu,
    )
    set_global_icon(icon)
    icon.run()
