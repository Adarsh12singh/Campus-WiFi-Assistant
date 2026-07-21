import time

from core.network_manager import connection_status
from core.login_manager import smart_login
from logger import write_log


def recover_connection():

    write_log("Recovery Started")

    for _ in range(5):

        status = connection_status()

        if status == "CONNECTED":

            write_log("Recovery Successful")

            return True

    result = smart_login()

    if result == "SUCCESS":

        print("✓ Recovery Successful")
        write_log("Recovery Successful")

        return True

    elif result == "DATA_LIMIT":

        print("⚠ Data Limit Exceeded")
        write_log("Data Limit Exceeded")

        return False

        time.sleep(10)

    write_log("Recovery Failed")

    return False