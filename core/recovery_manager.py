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

        if status == "CAPTIVE_PORTAL_OR_NO_INTERNET":

            if smart_login():

                return True

        time.sleep(10)

    write_log("Recovery Failed")

    return False