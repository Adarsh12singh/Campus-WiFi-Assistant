import time

from core.portal_login import login_to_portal
from core.network_manager import connection_status
from logger import write_log


def smart_login(max_attempts=3):
    """
    Attempts portal login and verifies whether internet
    becomes available afterwards.
    """

    for attempt in range(1, max_attempts + 1):

        print(f"========== LOGIN ATTEMPT {attempt} ==========")
        write_log(f"Login Attempt {attempt}")

        try:

            result = login_to_portal()

            # Portal itself reported something
            if result == "SUCCESS":

                print("Portal Login Submitted")

            elif result == "DATA_LIMIT":

                print("⚠ DATA LIMIT EXCEEDED")
                write_log("Data Limit Exceeded")
                return "DATA_LIMIT"

            else:

                print("Portal Login Failed")
                write_log("Portal Login Failed")

            # Give portal time to authenticate
            time.sleep(5)

            # Verify internet
            status = None

            for i in range(5):

                print(f"Checking Internet... {i+1}/5")

                status = connection_status()

                if status == "CONNECTED":
                    break

                time.sleep(3)

            if status == "CONNECTED":

                print("✓ LOGIN VERIFIED")
                write_log("Internet Verified")

                return "SUCCESS"

            print("Internet Still Not Available")
            write_log("Internet Verification Failed")

        except Exception as e:

            print("LOGIN ERROR:", e)
            write_log(f"Login Error: {e}")

        print("Waiting for portal authentication...")
        time.sleep(12)

    print("ALL LOGIN ATTEMPTS FAILED")
    write_log("All Login Attempts Failed")

    return "FAILED"