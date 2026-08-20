import os
import json
from app_paths import get_app_dir, get_resource_dir
from logger import write_log
from core.credential_manager import set_credential, get_credential

PROFILES_DIR = os.path.join(get_app_dir(), "profiles")


def get_profiles_dir():
    """Ensure profiles directory exists in app directory and return path."""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR, exist_ok=True)
    return PROFILES_DIR


def load_all_profiles():
    """
    Load all valid profile JSON files from the profiles directory.
    If no profiles exist, ensure default ou_hostels profile is created.
    """
    p_dir = get_profiles_dir()
    profiles = {}

    # Check app dir profiles
    for filename in os.listdir(p_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(p_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)
                    if isinstance(profile_data, dict) and "id" in profile_data:
                        profiles[profile_data["id"]] = profile_data
            except Exception as e:
                write_log(f"Error loading profile {filename}: {e}")

    # Fallback to default ou_hostels if empty
    if not profiles or "ou_hostels" not in profiles:
        default_profile = _create_default_ou_profile()
        profiles[default_profile["id"]] = default_profile

    return profiles


def get_profile_by_id(profile_id):
    """Retrieve a specific profile by its ID."""
    profiles = load_all_profiles()
    return profiles.get(profile_id)


def find_profile_by_ssid(ssid):
    """
    Find an enabled network profile matching the provided SSID.
    Returns the profile dict or None.
    """
    if not ssid:
        return None

    profiles = load_all_profiles()
    for profile in profiles.values():
        if profile.get("enabled", True) and profile.get("ssid") == ssid:
            return profile

    return None


def save_profile(profile_data):
    """Save or update a profile JSON file."""
    if not isinstance(profile_data, dict) or "id" not in profile_data:
        return False

    p_dir = get_profiles_dir()
    file_path = os.path.join(p_dir, f"{profile_data['id']}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4)
        return True
    except Exception as e:
        write_log(f"Error saving profile {profile_data['id']}: {e}")
        return False


def delete_profile(profile_id):
    """Delete a profile JSON file by profile ID."""
    p_dir = get_profiles_dir()
    file_path = os.path.join(p_dir, f"{profile_id}.json")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            write_log(f"Error deleting profile {profile_id}: {e}")
            return False
    return False


def _create_default_ou_profile():
    """Create default OU Hostels profile file if missing."""
    default_profile = {
        "id": "ou_hostels",
        "name": "OU Hostels",
        "ssid": "OU Hostels",
        "enabled": True,
        "login_strategy": "playwright",
        "portal_url": "http://172.16.1.1:8090/httpclient.html",
        "selectors": {
            "username": "#username",
            "password": "#password",
            "submit": "#loginbutton"
        },
        "data_limit_text": "data transfer has been exceeded",
        "verification_url": "http://www.msftconnecttest.com/connecttest.txt",
        "verification_expected": "Microsoft Connect Test",
        "credential_id": "ou_hostels_creds",
        "retry_count": 3,
        "retry_delay_seconds": 12
    }
    save_profile(default_profile)
    return default_profile


def migrate_legacy_config(legacy_config_path):
    """
    Migrates credentials and settings from legacy config.json into
    profiles/ou_hostels.json and credentials.json if present.
    """
    if not os.path.exists(legacy_config_path):
        return

    try:
        with open(legacy_config_path, "r", encoding="utf-8") as f:
            legacy_data = json.load(f)

        username = legacy_data.get("username", "")
        password = legacy_data.get("password", "")

        # Migrate credentials if non-empty and not yet saved
        existing_creds = get_credential("ou_hostels_creds")
        if username and (not existing_creds.get("username") or not existing_creds.get("password")):
            set_credential("ou_hostels_creds", username, password, "Migrated from legacy config.json")
            write_log("Migrated credentials from legacy config.json")

    except Exception as e:
        write_log(f"Legacy config migration error: {e}")
