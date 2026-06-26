import time

from core.portal_login import login_to_portal
from core.network_manager import verify_connection
from logger import write_log


def smart_login(max_attempts=3):

    for attempt in range(1, max_attempts + 1):

        write_log(f"Login Attempt {attempt}")

        try:

            login_to_portal()

            time.sleep(5)

            if verify_connection():

                write_log("Internet Verified")

                return True

            write_log("Internet Verification Failed")

        except Exception as e:

            write_log(f"Login Error: {e}")

        time.sleep(10)

    return False