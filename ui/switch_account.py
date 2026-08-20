import tkinter as tk
from tkinter import messagebox
from core.credential_manager import get_credential, set_credential
from core.network_manager import get_active_network_profile


def open_switch_account_window(target_credential_id=None):
    """
    Popup for quickly entering credentials for the active profile or a specified credential ID.
    """
    if target_credential_id is None:
        active_prof = get_active_network_profile()
        target_credential_id = active_prof.get("credential_id", "ou_hostels_creds") if active_prof else "ou_hostels_creds"

    window = tk.Tk()
    window.title("Switch Account / Credentials")
    window.geometry("340x220")
    window.resizable(False, False)

    try:
        window.attributes("-topmost", True)
    except Exception:
        pass

    current = get_credential(target_credential_id)

    header_label = tk.Label(window, text=f"Update: {target_credential_id}", font=("Segoe UI", 10, "bold"))
    header_label.pack(pady=(12, 5))

    tk.Label(window, text="Username / ID:", font=("Segoe UI", 9)).pack(anchor="w", padx=25)
    username_entry = tk.Entry(window, width=32, font=("Segoe UI", 10))
    username_entry.insert(0, current.get("username", ""))
    username_entry.pack(padx=25, pady=(0, 8))

    tk.Label(window, text="Password:", font=("Segoe UI", 9)).pack(anchor="w", padx=25)
    password_entry = tk.Entry(window, width=32, show="*", font=("Segoe UI", 10))
    password_entry.pack(padx=25, pady=(0, 12))
    password_entry.focus()

    def on_save():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.", parent=window)
            return

        set_credential(target_credential_id, username, password)

        messagebox.showinfo(
            "Saved",
            "Credentials updated successfully!\nThe assistant will re-attempt authentication shortly.",
            parent=window
        )
        window.destroy()

    def on_cancel():
        window.destroy()

    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Save", command=on_save, width=10, bg="#007acc", fg="white", font=("Segoe UI", 9, "bold")).pack(
        side="left", padx=6
    )
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10, font=("Segoe UI", 9)).pack(
        side="left", padx=6
    )

    window.mainloop()
