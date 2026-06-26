STARTING = "STARTING"
WAITING_FOR_WIFI = "WAITING_FOR_WIFI"
VERIFYING_NETWORK = "VERIFYING_NETWORK"
LOGIN_REQUIRED = "LOGIN_REQUIRED"
CONNECTED = "CONNECTED"
RECOVERY = "RECOVERY"


current_state = STARTING


def set_state(state):
    global current_state
    current_state = state


def get_state():
    return current_state