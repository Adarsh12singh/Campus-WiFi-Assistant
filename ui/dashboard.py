import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import os
import threading
import time

import app_state
from app_paths import get_app_dir
from core.state_manager import get_state
from core.profile_manager import load_all_profiles, save_profile, delete_profile, get_profile_by_id
from core.credential_manager import load_credentials, set_credential, delete_credential, mask_secret
from core.config_manager import get_config, save_config
from core.login_manager import smart_login
from startup_manager import is_in_startup, add_to_startup, remove_from_startup
from utils.wifi_name import get_current_wifi


class DashboardWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Campus WiFi Assistant — V3 Dashboard")
        self.root.geometry("700x520")
        self.root.minsize(650, 480)

        # Style configuration
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_overview = ttk.Frame(self.notebook)
        self.tab_profiles = ttk.Frame(self.notebook)
        self.tab_creds = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_overview, text=" 📊 Overview ")
        self.notebook.add(self.tab_profiles, text=" 🌐 Network Profiles ")
        self.notebook.add(self.tab_creds, text=" 🔑 Credentials ")
        self.notebook.add(self.tab_logs, text=" 📜 Live Logs ")
        self.notebook.add(self.tab_settings, text=" ⚙ Settings ")

        self._setup_overview_tab()
        self._setup_profiles_tab()
        self._setup_credentials_tab()
        self._setup_logs_tab()
        self._setup_settings_tab()

        self._is_alive = True
        self._start_periodic_refresh()

    def _setup_overview_tab(self):
        frame = ttk.LabelFrame(self.tab_overview, text="Real-Time Network Status", padding=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.lbl_ssid = ttk.Label(frame, text="Current WiFi: Detecting...", font=("Segoe UI", 11, "bold"))
        self.lbl_ssid.pack(anchor="w", pady=5)

        self.lbl_profile = ttk.Label(frame, text="Active Profile: None", font=("Segoe UI", 10))
        self.lbl_profile.pack(anchor="w", pady=5)

        self.lbl_status = ttk.Label(frame, text="Connection Status: Starting...", font=("Segoe UI", 10))
        self.lbl_status.pack(anchor="w", pady=5)

        self.lbl_state = ttk.Label(frame, text="Engine State: STARTING", font=("Segoe UI", 10))
        self.lbl_state.pack(anchor="w", pady=5)

        self.lbl_monitoring = ttk.Label(frame, text="Monitoring: Enabled", font=("Segoe UI", 10, "italic"))
        self.lbl_monitoring.pack(anchor="w", pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        self.btn_login = ttk.Button(btn_frame, text="⚡ Authenticate Now", command=self._on_manual_login)
        self.btn_login.pack(side="left", padx=5)

        self.btn_toggle_monitor = ttk.Button(btn_frame, text="⏸ Pause Monitoring", command=self._toggle_monitoring)
        self.btn_toggle_monitor.pack(side="left", padx=5)

        self.btn_refresh = ttk.Button(btn_frame, text="🔄 Refresh", command=self._refresh_overview)
        self.btn_refresh.pack(side="left", padx=5)

    def _setup_profiles_tab(self):
        frame = ttk.Frame(self.tab_profiles, padding=10)
        frame.pack(fill="both", expand=True)

        cols = ("id", "name", "ssid", "strategy", "enabled", "credential_id")
        self.tree_profiles = ttk.Treeview(frame, columns=cols, show="headings", height=10)

        self.tree_profiles.heading("id", text="Profile ID")
        self.tree_profiles.heading("name", text="Display Name")
        self.tree_profiles.heading("ssid", text="Target SSID")
        self.tree_profiles.heading("strategy", text="Strategy")
        self.tree_profiles.heading("enabled", text="Enabled")
        self.tree_profiles.heading("credential_id", text="Credential Reference")

        self.tree_profiles.column("id", width=100)
        self.tree_profiles.column("name", width=120)
        self.tree_profiles.column("ssid", width=110)
        self.tree_profiles.column("strategy", width=90)
        self.tree_profiles.column("enabled", width=70)
        self.tree_profiles.column("credential_id", width=130)

        self.tree_profiles.pack(fill="both", expand=True)

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill="x", pady=10)

        ttk.Button(btn_bar, text="➕ Add Profile", command=self._add_profile_dialog).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="✏ Edit Profile", command=self._edit_profile_dialog).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="Toggle Enabled", command=self._toggle_profile_enabled).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="🗑 Delete Profile", command=self._delete_selected_profile).pack(side="left", padx=4)

        self._refresh_profiles_list()

    def _setup_credentials_tab(self):
        frame = ttk.Frame(self.tab_creds, padding=10)
        frame.pack(fill="both", expand=True)

        cols = ("id", "username", "password", "description")
        self.tree_creds = ttk.Treeview(frame, columns=cols, show="headings", height=10)

        self.tree_creds.heading("id", text="Credential ID")
        self.tree_creds.heading("username", text="Username / ID")
        self.tree_creds.heading("password", text="Password (Masked)")
        self.tree_creds.heading("description", text="Description")

        self.tree_creds.column("id", width=130)
        self.tree_creds.column("username", width=130)
        self.tree_creds.column("password", width=120)
        self.tree_creds.column("description", width=220)

        self.tree_creds.pack(fill="both", expand=True)

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill="x", pady=10)

        ttk.Button(btn_bar, text="➕ Add / Update Credential", command=self._add_edit_credential_dialog).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="🗑 Delete Credential", command=self._delete_credential).pack(side="left", padx=4)

        self._refresh_credentials_list()

    def _setup_logs_tab(self):
        frame = ttk.Frame(self.tab_logs, padding=10)
        frame.pack(fill="both", expand=True)

        self.txt_logs = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.txt_logs.pack(fill="both", expand=True)

        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill="x", pady=8)

        ttk.Button(btn_bar, text="🔄 Refresh Logs", command=self._refresh_logs).pack(side="left", padx=4)
        ttk.Button(btn_bar, text="🧹 Clear Log File", command=self._clear_logs).pack(side="left", padx=4)

        self._refresh_logs()

    def _setup_settings_tab(self):
        frame = ttk.LabelFrame(self.tab_settings, text="Application Settings", padding=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.var_startup = tk.BooleanVar(value=is_in_startup())
        chk_startup = ttk.Checkbutton(frame, text="Start Campus WiFi Assistant with Windows", variable=self.var_startup)
        chk_startup.pack(anchor="w", pady=8)

        config = get_config()
        self.var_autoconnect = tk.BooleanVar(value=config.get("wifi_autoconnect_enabled", True))
        chk_auto = ttk.Checkbutton(frame, text="Auto-connect to preferred WiFi if disconnected", variable=self.var_autoconnect)
        chk_auto.pack(anchor="w", pady=8)

        ttk.Label(frame, text="Monitoring Interval (seconds):").pack(anchor="w", pady=(10, 2))
        self.entry_interval = ttk.Entry(frame, width=10)
        self.entry_interval.insert(0, str(config.get("check_interval_seconds", 15)))
        self.entry_interval.pack(anchor="w", pady=(0, 15))

        ttk.Button(frame, text="💾 Save Settings", command=self._save_settings).pack(anchor="w", pady=5)

    def _refresh_overview(self):
        ssid = get_current_wifi() or "No WiFi Connected"
        state = get_state()
        status = app_state.current_status
        prof_name = app_state.current_profile_name or "None"

        self.lbl_ssid.config(text=f"Current WiFi: {ssid}")
        self.lbl_profile.config(text=f"Active Profile: {prof_name}")
        self.lbl_status.config(text=f"Connection Status: {status}")
        self.lbl_state.config(text=f"Engine State: {state}")

        if app_state.monitoring_enabled:
            self.lbl_monitoring.config(text="Monitoring: Active (Running)")
            self.btn_toggle_monitor.config(text="⏸ Pause Monitoring")
        else:
            self.lbl_monitoring.config(text="Monitoring: Paused")
            self.btn_toggle_monitor.config(text="▶ Resume Monitoring")

    def _refresh_profiles_list(self):
        for item in self.tree_profiles.get_children():
            self.tree_profiles.delete(item)

        profiles = load_all_profiles()
        for p in profiles.values():
            self.tree_profiles.insert("", "end", values=(
                p.get("id"),
                p.get("name"),
                p.get("ssid"),
                p.get("login_strategy", "playwright"),
                "Yes" if p.get("enabled", True) else "No",
                p.get("credential_id", "")
            ))

    def _refresh_credentials_list(self):
        for item in self.tree_creds.get_children():
            self.tree_creds.delete(item)

        creds = load_credentials()
        for cid, data in creds.items():
            self.tree_creds.insert("", "end", values=(
                cid,
                data.get("username", ""),
                mask_secret(data.get("password", "")),
                data.get("description", "")
            ))

    def _refresh_logs(self):
        log_path = os.path.join(get_app_dir(), "logs.txt")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    content = "".join(lines[-150:])  # last 150 lines
                self.txt_logs.delete("1.0", tk.END)
                self.txt_logs.insert(tk.END, content)
                self.txt_logs.see(tk.END)
            except Exception:
                pass

    def _clear_logs(self):
        log_path = os.path.join(get_app_dir(), "logs.txt")
        if messagebox.askyesno("Confirm", "Clear logs.txt?", parent=self.root):
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("")
                self._refresh_logs()
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear logs: {e}", parent=self.root)

    def _on_manual_login(self):
        def _task():
            self.btn_login.config(state="disabled")
            smart_login()
            self.root.after(100, lambda: self.btn_login.config(state="normal"))
            self.root.after(100, self._refresh_overview)

        threading.Thread(target=_task, daemon=True).start()

    def _toggle_monitoring(self):
        app_state.monitoring_enabled = not app_state.monitoring_enabled
        self._refresh_overview()

    def _toggle_profile_enabled(self):
        selected = self.tree_profiles.selection()
        if not selected:
            messagebox.showwarning("Select Profile", "Please select a profile first.", parent=self.root)
            return
        item_vals = self.tree_profiles.item(selected[0], "values")
        pid = item_vals[0]
        p = get_profile_by_id(pid)
        if p:
            p["enabled"] = not p.get("enabled", True)
            save_profile(p)
            self._refresh_profiles_list()

    def _delete_selected_profile(self):
        selected = self.tree_profiles.selection()
        if not selected:
            return
        pid = self.tree_profiles.item(selected[0], "values")[0]
        if pid == "ou_hostels":
            messagebox.showwarning("Protected Profile", "Default OU Hostels profile cannot be deleted.", parent=self.root)
            return
        if messagebox.askyesno("Confirm Delete", f"Delete profile '{pid}'?", parent=self.root):
            delete_profile(pid)
            self._refresh_profiles_list()

    def _add_profile_dialog(self):
        self._open_profile_editor(None)

    def _edit_profile_dialog(self):
        selected = self.tree_profiles.selection()
        if not selected:
            messagebox.showwarning("Select Profile", "Please select a profile to edit.", parent=self.root)
            return
        pid = self.tree_profiles.item(selected[0], "values")[0]
        profile = get_profile_by_id(pid)
        if profile:
            self._open_profile_editor(profile)

    def _open_profile_editor(self, profile):
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit Profile" if profile else "Add New Network Profile")
        dlg.geometry("420x460")
        dlg.transient(self.root)
        dlg.grab_set()

        fields = [
            ("Profile ID:", profile.get("id", "") if profile else ""),
            ("Display Name:", profile.get("name", "") if profile else ""),
            ("Target SSID:", profile.get("ssid", "") if profile else ""),
            ("Strategy (playwright / http_post / none):", profile.get("login_strategy", "playwright") if profile else "playwright"),
            ("Portal URL:", profile.get("portal_url", "") if profile else ""),
            ("Credential ID reference:", profile.get("credential_id", "ou_hostels_creds") if profile else "ou_hostels_creds"),
            ("Quota text indicator:", profile.get("data_limit_text", "data transfer has been exceeded") if profile else "data transfer has been exceeded")
        ]

        entries = {}
        for idx, (lbl_text, val) in enumerate(fields):
            ttk.Label(dlg, text=lbl_text).pack(anchor="w", padx=20, pady=(8, 2))
            entry = ttk.Entry(dlg, width=38)
            entry.insert(0, val)
            if profile and idx == 0:
                entry.config(state="disabled")
            entry.pack(anchor="w", padx=20)
            entries[lbl_text] = entry

        def on_save_prof():
            pid = entries["Profile ID:"].get().strip()
            name = entries["Display Name:"].get().strip()
            ssid = entries["Target SSID:"].get().strip()
            strat = entries["Strategy (playwright / http_post / none):"].get().strip().lower()
            url = entries["Portal URL:"].get().strip()
            cid = entries["Credential ID reference:"].get().strip()
            quota = entries["Quota text indicator:"].get().strip()

            if not pid or not ssid:
                messagebox.showerror("Error", "Profile ID and SSID are required.", parent=dlg)
                return

            prof_obj = profile.copy() if profile else {}
            prof_obj.update({
                "id": pid,
                "name": name or pid,
                "ssid": ssid,
                "login_strategy": strat or "playwright",
                "portal_url": url,
                "credential_id": cid or "ou_hostels_creds",
                "data_limit_text": quota,
                "enabled": prof_obj.get("enabled", True),
                "selectors": prof_obj.get("selectors", {
                    "username": "#username",
                    "password": "#password",
                    "submit": "#loginbutton"
                }),
                "verification_url": "http://www.msftconnecttest.com/connecttest.txt",
                "verification_expected": "Microsoft Connect Test"
            })

            save_profile(prof_obj)
            self._refresh_profiles_list()
            dlg.destroy()

        btn_f = ttk.Frame(dlg)
        btn_f.pack(pady=20)
        ttk.Button(btn_f, text="Save Profile", command=on_save_prof).pack(side="left", padx=5)
        ttk.Button(btn_f, text="Cancel", command=dlg.destroy).pack(side="left", padx=5)

    def _add_edit_credential_dialog(self):
        cid = simpledialog.askstring("Credential ID", "Enter Credential ID (e.g. ou_hostels_creds):", parent=self.root)
        if not cid:
            return
        user = simpledialog.askstring("Username", f"Enter Username for {cid}:", parent=self.root)
        if user is None:
            return
        pwd = simpledialog.askstring("Password", f"Enter Password for {cid}:", show="*", parent=self.root)
        if pwd is None:
            return
        desc = simpledialog.askstring("Description", "Enter description (optional):", parent=self.root) or ""

        set_credential(cid, user, pwd, desc)
        self._refresh_credentials_list()

    def _delete_credential(self):
        selected = self.tree_creds.selection()
        if not selected:
            return
        cid = self.tree_creds.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete credential '{cid}'?", parent=self.root):
            delete_credential(cid)
            self._refresh_credentials_list()

    def _save_settings(self):
        try:
            interval = int(self.entry_interval.get().strip())
        except ValueError:
            interval = 15

        cfg = get_config()
        cfg["wifi_autoconnect_enabled"] = self.var_autoconnect.get()
        cfg["check_interval_seconds"] = interval
        save_config(cfg)

        if self.var_startup.get():
            add_to_startup()
        else:
            remove_from_startup()

        messagebox.showinfo("Saved", "Settings updated successfully!", parent=self.root)

    def _start_periodic_refresh(self):
        def _loop():
            while self._is_alive:
                try:
                    self.root.after(0, self._refresh_overview)
                except Exception:
                    break
                time.sleep(3)

        threading.Thread(target=_loop, daemon=True).start()

    def show(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._is_alive = False
        self.root.destroy()


def open_dashboard():
    """Launch the dashboard in a separate thread or main thread safely."""
    try:
        app = DashboardWindow()
        app.show()
    except Exception as e:
        print(f"Error opening Dashboard: {e}")
