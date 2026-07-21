import json
import os

from app_paths import get_app_dir


CONFIG_PATH = os.path.join(get_app_dir(), "config.json")

DEFAULT_CONFIG = {
    "portal_url": "http://172.16.1.1:8090/httpclient.html",
    "username": "",
    "password": "",
    "target_wifi": "OU Hostels",
    "monitoring_enabled": True,
    "wifi_autoconnect_enabled": True
}


def _create_default_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def get_config():

    if not os.path.exists(CONFIG_PATH):
        _create_default_config()

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:

        return json.load(file)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def get_value(key):

    return get_config().get(key)