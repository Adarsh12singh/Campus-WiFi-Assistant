# Campus WiFi Assistant (V3)

Automates campus & hostel WiFi connection, multi-network detection, and captive portal authentication on Windows.

## 🚀 Features (V3)

* **Multi-Network Profile System**: Dynamic profile support (`profiles/*.json`) for multiple universities, hostels, and campuses.
* **Modular Authentication Strategies**:
  * `PlaywrightStrategy`: Full headless/browser automation for JavaScript-heavy captive portals (OU Hostels).
  * `HttpStrategy`: High-speed HTTP POST form authentication for lightweight portals.
  * `NoAuthStrategy`: Safe pass-through for direct open networks.
* **Separated Credential Management**: Decoupled credential storage (`credentials.json`) with password masking in logs and UI.
* **Centralized State Machine**: 10 distinct connection and authentication states with reactive listener hooks.
* **Desktop Dashboard (GUI)**: Multi-tab management interface for real-time status, network profile editing, credential management, live logs, and settings.
* **Windows System Tray & Startup**: Unobtrusive background operation, wake-from-sleep recovery, and delayed Windows Startup integration.
* **Daily Quota Management**: Detects data limit exceeded states and pauses repetitive logins until credentials change.
* **Desktop Toast Notifications**: Real-time status notifications for connections, errors, and state changes.

---

## 📁 Project Structure

```text
campus wifi assistant/
├── main.py                  # Main controller & background monitoring loop
├── app_paths.py             # Smart path resolver (Dev vs Frozen PyInstaller .exe)
├── app_state.py             # Shared application runtime state
├── startup_manager.py       # Windows Startup folder integration
├── logger.py                # Timestamped logging (logs.txt)
├── main.spec                # PyInstaller build specification
├── config.json              # Global application settings
├── credentials.json         # Decoupled credential store
│
├── profiles/                # Network profile configurations
│   ├── ou_hostels.json      # Default profile for OU Hostels
│   └── university_example.json # Extensible template profile
│
├── core/
│   ├── profile_manager.py   # Multi-network profile discovery & CRUD
│   ├── credential_manager.py# Credential storage & secret masking
│   ├── state_manager.py     # Centralized connection state machine
│   ├── network_manager.py   # Dynamic SSID matching & internet checking
│   ├── portal_state.py      # Captive portal detection (NCSI probing)
│   ├── login_manager.py     # Smart login orchestrator with exponential retries
│   ├── config_manager.py    # Global configuration & legacy migration
│   └── strategies/          # Modular login strategy engine
│       ├── base.py          # Abstract BaseLoginStrategy
│       ├── playwright_strategy.py # Playwright browser automation
│       ├── http_strategy.py # HTTP POST form login strategy
│       └── factory.py       # Strategy factory & registry
│
├── ui/
│   ├── dashboard.py         # Multi-tab Tkinter dashboard UI
│   ├── tray_app.py          # Windows System Tray interface (pystray)
│   ├── switch_account.py    # Quick credential switcher
│   └── notification_manager.py # Windows toast notifications (plyer)
│
├── utils/
│   ├── wifi_name.py         # Current SSID detection (netsh)
│   └── wifi_autoconnect.py  # Automated WiFi reconnection (netsh)
│
└── tests/
    └── test_v3_core.py      # Unit tests for profiles, creds, strategies, and state
```

---

## 🛠 Installation & Usage

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirement.txt
   playwright install chromium
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 📦 Build Standalone Executable (.exe)

```bash
pyinstaller main.spec
```

The output executable will be created in `dist/CampusWiFiAssistant.exe`.

---

## 🗺 Roadmap

* **V1 (Complete)**: Core automation & captive portal login for OU Hostels.
* **V2 (Complete)**: Autonomous Windows background process, system tray, and startup launcher.
* **V3 (Complete)**: Multi-network profiles, modular login strategies, credential decoupling, desktop dashboard.
* **V4 (Planned)**: Intelligent network quality monitoring, adaptive recovery, and connection analytics.
* **V5 (Planned)**: Cloud configuration sync & multi-device platform.
* **V6 (Planned)**: Cross-platform support (Linux, macOS, Android).
* **V7 (Planned)**: University-scale multi-campus production platform.

---

## 👤 Author
**Adarsh Singh**
