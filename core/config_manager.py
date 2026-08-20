import json
import os
from app_paths import get_app_dir
from core.profile_manager import migrate_legacy_config

CONFIG_PATH = os.path.join(get_app_dir(), "config.json")

DEFAULT_CONFIG = {
    "monitoring_enabled": True,
    "wifi_autoconnect_enabled": True,
    "check_interval_seconds": 15,
    "notifications_enabled": True,
    "preferred_target_wifi": "OU Hostels"
}


def _create_default_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)


def get_config():
    """Load configuration, initializing defaults and performing migrations if needed."""
    if not os.path.exists(CONFIG_PATH):
        _create_default_config()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            # Trigger migration if legacy keys present
            if "username" in data or "portal_url" in data:
                migrate_legacy_config(CONFIG_PATH)
            return data
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save global application settings to config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def get_value(key, default=None):
    return get_config().get(key, default)