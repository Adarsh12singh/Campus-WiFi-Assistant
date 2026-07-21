import requests


def login_required():
    """
    Returns False if real internet access is confirmed.
    Returns True if the captive portal is still blocking traffic
    (or the check itself fails, to be safe).

    This replaces the old approach of loading the portal page and
    looking for "Logout" text, which was unreliable because the
    portal doesn't always show that text after a successful login.
    """

    try:
        response = requests.get(
            "http://www.msftconnecttest.com/connecttest.txt",
            allow_redirects=False,
            timeout=5
        )

        # Microsoft's NCSI endpoint returns exactly this body when
        # there is no captive portal intercepting traffic.
        if response.status_code == 200 and response.text.strip() == "Microsoft Connect Test":
            return False

        return True

    except Exception:
        return True