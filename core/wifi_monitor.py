import psutil
import requests

def wifi_connected():
    stats = psutil.net_if_stats()

    for interface, data in stats.items():
        if data.isup:
            return True

    return False


def internet_available():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False


def connection_status():

    wifi = wifi_connected()
    internet = internet_available()

    if not wifi:
        return "WIFI_DISCONNECTED"

    if wifi and not internet:
        return "CAPTIVE_PORTAL_OR_NO_INTERNET"

    return "CONNECTED"