import time

from utils.wifi_name import get_current_wifi
from core.portal_state import login_required

TARGET_WIFI = "OU Hostels"


def wifi_connected():
    """
    Returns True only if connected to the target hostel WiFi.
    """
    return get_current_wifi() == TARGET_WIFI


def wait_for_stable_network(timeout=60):

    start = time.time()

    while time.time() - start < timeout:

        if wifi_connected():
            return True

        time.sleep(2)

    return False


def connection_status():

    if not wifi_connected():
        return "WIFI_DISCONNECTED"

    try:

        if login_required():
            return "CAPTIVE_PORTAL_OR_NO_INTERNET"

        return "CONNECTED"

    except Exception as e:

        print("Portal State Error:", e)

        return "CAPTIVE_PORTAL_OR_NO_INTERNET"