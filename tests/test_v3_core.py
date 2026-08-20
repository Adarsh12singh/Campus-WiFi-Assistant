import unittest
import os
import sys

# Ensure root project path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profile_manager import (
    load_all_profiles,
    find_profile_by_ssid,
    save_profile,
    delete_profile,
    get_profile_by_id
)
from core.credential_manager import (
    load_credentials,
    get_credential,
    set_credential,
    delete_credential,
    mask_secret
)
from core.strategies.factory import get_login_strategy
from core.strategies.playwright_strategy import PlaywrightStrategy
from core.strategies.http_strategy import HttpStrategy
from core.strategies.base import LoginResult
from core.state_manager import (
    set_state,
    get_state,
    register_state_listener,
    unregister_state_listener,
    DISCONNECTED,
    WIFI_CONNECTED,
    INTERNET_CONNECTED,
    UNKNOWN_NETWORK
)


class TestV3Core(unittest.TestCase):

    def test_profile_manager(self):
        # 1. Load profiles (OU Hostels default should exist)
        profiles = load_all_profiles()
        self.assertIn("ou_hostels", profiles)
        ou_prof = profiles["ou_hostels"]
        self.assertEqual(ou_prof.get("ssid"), "OU Hostels")
        self.assertEqual(ou_prof.get("login_strategy"), "playwright")

        # 2. Find by SSID
        matched = find_profile_by_ssid("OU Hostels")
        self.assertIsNotNone(matched)
        self.assertEqual(matched["id"], "ou_hostels")

        # 3. Unknown SSID
        unknown = find_profile_by_ssid("RandomCoffeeShopWiFi_999")
        self.assertIsNone(unknown)

        # 4. Save and delete temporary test profile
        test_prof = {
            "id": "unit_test_prof",
            "name": "Unit Test WiFi",
            "ssid": "TestSSID_XYZ",
            "enabled": True,
            "login_strategy": "http_post",
            "portal_url": "http://1.2.3.4/login",
            "credential_id": "test_creds"
        }
        self.assertTrue(save_profile(test_prof))
        loaded = get_profile_by_id("unit_test_prof")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["name"], "Unit Test WiFi")

        # Cleanup
        self.assertTrue(delete_profile("unit_test_prof"))
        self.assertIsNone(get_profile_by_id("unit_test_prof"))

    def test_credential_manager(self):
        # 1. Secret masking
        self.assertEqual(mask_secret(""), "")
        self.assertEqual(mask_secret("ab"), "***")
        self.assertEqual(mask_secret("password123"), "p*********3")

        # 2. Set and retrieve credential
        set_credential("test_unit_cred", "testuser", "secretpass123", "Test cred")
        cred = get_credential("test_unit_cred")
        self.assertEqual(cred.get("username"), "testuser")
        self.assertEqual(cred.get("password"), "secretpass123")

        # 3. Delete credential
        self.assertTrue(delete_credential("test_unit_cred"))
        empty_cred = get_credential("test_unit_cred")
        self.assertEqual(empty_cred.get("username"), "")

    def test_strategy_factory(self):
        # Playwright
        s1 = get_login_strategy("playwright")
        self.assertIsInstance(s1, PlaywrightStrategy)
        self.assertEqual(s1.name, "playwright")

        # HTTP
        s2 = get_login_strategy("http_post")
        self.assertIsInstance(s2, HttpStrategy)
        self.assertEqual(s2.name, "http_post")

        # None / Fallback
        s3 = get_login_strategy("none")
        self.assertEqual(s3.name, "none")
        self.assertEqual(s3.login({}, {}), LoginResult.SUCCESS)

    def test_state_machine_and_listeners(self):
        history = []

        def on_change(old_state, new_state):
            history.append((old_state, new_state))

        register_state_listener(on_change)

        set_state(DISCONNECTED)
        self.assertEqual(get_state(), DISCONNECTED)

        set_state(WIFI_CONNECTED)
        self.assertEqual(get_state(), WIFI_CONNECTED)

        set_state(INTERNET_CONNECTED)
        self.assertEqual(get_state(), INTERNET_CONNECTED)

        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[-1], (WIFI_CONNECTED, INTERNET_CONNECTED))

        unregister_state_listener(on_change)


if __name__ == "__main__":
    unittest.main()
