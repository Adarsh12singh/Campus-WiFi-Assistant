import time
from ui.icon_holder import get_global_icon

_last_notif_time = 0
_last_notif_msg = ""


def show_notification(title, message):
    """
    Safely display a Windows toast/balloon notification.
    Uses native pystray.notify if tray is active, falls back to plyer with safe error handling.
    """
    global _last_notif_time, _last_notif_msg
    now = time.time()

    # Prevent spamming identical notifications in rapid succession
    if message == _last_notif_msg and (now - _last_notif_time) < 3:
        return

    _last_notif_time = now
    _last_notif_msg = message

    # Try pystray native notify first
    icon = get_global_icon()
    if icon is not None:
        try:
            icon.notify(message, title)
            return
        except Exception:
            pass

    # Fallback to plyer safely
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Campus WiFi Assistant",
            timeout=4
        )
    except Exception as e:
        # Ignore balloon tip collision errors quietly
        pass