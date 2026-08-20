import requests

DEFAULT_VERIFICATION_URL = "http://www.msftconnecttest.com/connecttest.txt"
DEFAULT_EXPECTED_BODY = "Microsoft Connect Test"


def login_required(verification_url=None, expected_body=None):
    """
    Returns False if real internet access is confirmed.
    Returns True if the captive portal is still intercepting traffic.
    """
    url = verification_url or DEFAULT_VERIFICATION_URL
    expected = expected_body or DEFAULT_EXPECTED_BODY

    try:
        response = requests.get(
            url,
            allow_redirects=False,
            timeout=5
        )

        if response.status_code == 200 and expected in response.text.strip():
            return False

        return True

    except Exception:
        return True