import time
from utils.wifi_name import get_current_wifi
from core.portal_state import login_required
from core.profile_manager import find_profile_by_ssid, load_all_profiles
from core.state_manager import (
    set_state,
    DISCONNECTED,
    WIFI_CONNECTED,
    CHECKING_INTERNET,
    CAPTIVE_PORTAL,
    INTERNET_CONNECTED,
    UNKNOWN_NETWORK
)


def get_active_network_profile():
    """
    Returns the loaded profile matching the currently connected WiFi SSID, or None.
    """
    current_ssid = get_current_wifi()
    if not current_ssid:
        return None
    return find_profile_by_ssid(current_ssid)


def wifi_connected():
    """Returns True if any WiFi network is currently connected."""
    return get_current_wifi() is not None


def wait_for_stable_network(target_ssid=None, timeout=60):
    """Wait until connected to target WiFi SSID, or any known WiFi if none specified."""
    start = time.time()
    while time.time() - start < timeout:
        current = get_current_wifi()
        if current:
            if target_ssid is None or current == target_ssid:
                return True
        time.sleep(2)
    return False


def connection_status(profile=None):
    """
    Evaluate current connection status:
    - 'WIFI_DISCONNECTED' if not connected to any WiFi
    - 'UNKNOWN_NETWORK' if connected to a WiFi with no matching enabled profile
    - 'CAPTIVE_PORTAL_OR_NO_INTERNET' if portal blocks traffic
    - 'CONNECTED' if internet is confirmed
    """
    current_ssid = get_current_wifi()
    if not current_ssid:
        set_state(DISCONNECTED)
        return "WIFI_DISCONNECTED"

    active_profile = profile or find_profile_by_ssid(current_ssid)

    if not active_profile:
        # Unknown network - check if it has internet directly
        if not login_required():
            set_state(INTERNET_CONNECTED)
            return "CONNECTED"
        set_state(UNKNOWN_NETWORK)
        return "UNKNOWN_NETWORK"

    set_state(CHECKING_INTERNET)
    try:
        v_url = active_profile.get("verification_url")
        v_exp = active_profile.get("verification_expected")

        if login_required(v_url, v_exp):
            set_state(CAPTIVE_PORTAL)
            return "CAPTIVE_PORTAL_OR_NO_INTERNET"

        set_state(INTERNET_CONNECTED)
        return "CONNECTED"

    except Exception as e:
        print("Portal State Check Error:", e)
        set_state(CAPTIVE_PORTAL)
        return "CAPTIVE_PORTAL_OR_NO_INTERNET"