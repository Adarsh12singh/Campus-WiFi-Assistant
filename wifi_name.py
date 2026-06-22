import subprocess

def get_current_wifi():

    try:
        output = subprocess.check_output(
            "netsh wlan show interfaces",
            shell=True
        ).decode("utf-8", errors="ignore")

        for line in output.split("\n"):

            if "SSID" in line and "BSSID" not in line:

                return line.split(":")[1].strip()

    except:
        return None

    return None