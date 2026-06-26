import time
import requests
import psutil


def wifi_connected():
    stats = psutil.net_if_stats()

    for interface, data in stats.items():
        if data.isup:
            return True

    return False


def internet_available():

    try:
        requests.get(
            "https://clients3.google.com/generate_204",
            timeout=5
        )
        return True

    except:
        return False


def wait_for_stable_network(seconds=20):

    start = time.time()

    while time.time() - start < seconds:

        if not wifi_connected():
            return False

        time.sleep(1)

    return True


def verify_connection(retries=3):

    for _ in range(retries):

        if internet_available():
            return True

        time.sleep(3)

    return False


def connection_status():

    if not wifi_connected():
        return "WIFI_DISCONNECTED"

    if verify_connection():
        return "CONNECTED"

    return "CAPTIVE_PORTAL_OR_NO_INTERNET"