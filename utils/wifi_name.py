import subprocess

def get_current_wifi():

    try:
        output = subprocess.check_output(
            "netsh wlan show interfaces",
            shell=True
        ).decode("utf-8", errors="ignore")

        for line in output.splitlines():

            line = line.strip()

            if line.startswith("SSID") and "BSSID" not in line:
                return line.split(":", 1)[1].strip()

    except Exception:
        return None

    return None