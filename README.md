# Campus WiFi Assistant

Automates hostel WiFi connection and captive portal authentication on Windows.

## Features

* Automatic WiFi connection
* Automatic captive portal login
* System tray integration
* Real-time status monitoring
* Desktop notifications
* Logging system
* Configurable credentials

## Technologies Used

* Python
* PyStray
* Pillow
* Requests
* PyInstaller
* Windows Netsh

## Project Structure

```text
main.py                  # Main controller
wifi_monitor.py          # Internet and WiFi monitoring
wifi_name.py             # Detect current SSID
wifi_autoconnect.py      # Auto-connect to target WiFi
portal_login.py          # Portal authentication
tray_app.py              # System tray interface
notification_manager.py  # Notifications
logger.py                # Logging
app_state.py             # Shared application state
config.example.json      # Sample configuration
```

## Installation

1. Clone repository
2. Install requirements
3. Create config.json
4. Run:

```bash
python main.py
```

## Build EXE

```bash
pyinstaller main.spec
```

## Future Roadmap

### v2.0

* Multiple credential support
* Multiple WiFi profiles
* GUI dashboard
* Login statistics
* Installer package

### v3.0

* Android application
* Cloud synchronization
* Centralized management
* Analytics dashboard

## Author

Adarsh Singh
