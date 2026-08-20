import json
import os
from app_paths import get_app_dir
from logger import write_log

CREDENTIALS_FILE = os.path.join(get_app_dir(), "credentials.json")


def _get_default_credentials():
    return {
        "ou_hostels_creds": {
            "username": "",
            "password": "",
            "description": "Default credentials for OU Hostels"
        }
    }


def load_credentials():
    """Load credentials from credentials.json, creating defaults if missing."""
    if not os.path.exists(CREDENTIALS_FILE):
        creds = _get_default_credentials()
        save_all_credentials(creds)
        return creds

    try:
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        write_log(f"Error loading credentials: {e}")
        return _get_default_credentials()


def save_all_credentials(credentials_dict):
    """Save the full credentials dictionary to credentials.json."""
    try:
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(credentials_dict, f, indent=4)
        return True
    except Exception as e:
        write_log(f"Error saving credentials: {e}")
        return False


def get_credential(credential_id):
    """Retrieve username and password for a specific credential ID."""
    if not credential_id:
        return {"username": "", "password": ""}

    creds = load_credentials()
    return creds.get(credential_id, {"username": "", "password": ""})


def set_credential(credential_id, username, password, description=""):
    """Create or update a specific credential entry."""
    creds = load_credentials()
    creds[credential_id] = {
        "username": username,
        "password": password,
        "description": description or creds.get(credential_id, {}).get("description", "")
    }
    return save_all_credentials(creds)


def delete_credential(credential_id):
    """Delete a credential entry if it exists."""
    creds = load_credentials()
    if credential_id in creds:
        del creds[credential_id]
        return save_all_credentials(creds)
    return False


def list_credentials():
    """Return list of credential IDs and descriptions (with passwords masked)."""
    creds = load_credentials()
    result = []
    for cid, data in creds.items():
        result.append({
            "id": cid,
            "username": data.get("username", ""),
            "masked_password": mask_secret(data.get("password", "")),
            "description": data.get("description", "")
        })
    return result


def mask_secret(secret_str):
    """Mask a secret string for safe display or logging (e.g., 'p******d')."""
    if not secret_str:
        return ""
    if len(secret_str) <= 2:
        return "***"
    return secret_str[0] + "*" * (len(secret_str) - 2) + secret_str[-1]
