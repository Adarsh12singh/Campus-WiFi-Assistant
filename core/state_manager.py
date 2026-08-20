# Connection State Constants
DISCONNECTED = "DISCONNECTED"
WIFI_CONNECTING = "WIFI_CONNECTING"
WIFI_CONNECTED = "WIFI_CONNECTED"
CHECKING_INTERNET = "CHECKING_INTERNET"
CAPTIVE_PORTAL = "CAPTIVE_PORTAL"
AUTHENTICATING = "AUTHENTICATING"
AUTHENTICATED = "AUTHENTICATED"
INTERNET_CONNECTED = "INTERNET_CONNECTED"
DATA_LIMIT_EXCEEDED = "DATA_LIMIT_EXCEEDED"
UNKNOWN_NETWORK = "UNKNOWN_NETWORK"
RECOVERY = "RECOVERY"
MONITORING_PAUSED = "MONITORING_PAUSED"

# Legacy aliases for backward compatibility
STARTING = "STARTING"
WAITING_FOR_WIFI = DISCONNECTED
VERIFYING_NETWORK = CHECKING_INTERNET
LOGIN_REQUIRED = CAPTIVE_PORTAL
CONNECTED = INTERNET_CONNECTED

current_state = STARTING
_state_listeners = []


def register_state_listener(callback):
    """Register a callback function fn(old_state, new_state) called on state change."""
    if callback not in _state_listeners:
        _state_listeners.append(callback)


def unregister_state_listener(callback):
    """Remove a registered state listener."""
    if callback in _state_listeners:
        _state_listeners.remove(callback)


def set_state(state):
    """Update system state and notify listeners."""
    global current_state
    if current_state != state:
        old_state = current_state
        current_state = state
        for listener in _state_listeners:
            try:
                listener(old_state, new_state=state)
            except Exception:
                pass


def get_state():
    """Return the current application state."""
    return current_state