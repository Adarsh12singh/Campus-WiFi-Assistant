import tkinter as tk
from tkinter import messagebox

from core.config_manager import get_config, save_config


def _save_credentials(username, password):
    config = get_config()

    config["username"] = username
    config["password"] = password

    save_config(config)


def open_switch_account_window():
    """
    Small popup for manually entering the next account's credentials.
    This does NOT store or pick between multiple accounts on its own -
    it just saves whatever single username/password you type in, the
    same as hand-editing config.json, only faster.
    """

    window = tk.Tk()
    window.title("Switch Account")
    window.geometry("300x180")
    window.resizable(False, False)

    try:
        window.attributes("-topmost", True)
    except Exception:
        pass

    current = get_config()

    tk.Label(window, text="Username").pack(pady=(15, 0))
    username_entry = tk.Entry(window, width=30)
    username_entry.insert(0, current.get("username", ""))
    username_entry.pack()

    tk.Label(window, text="Password").pack(pady=(10, 0))
    password_entry = tk.Entry(window, width=30, show="*")
    password_entry.pack()
    password_entry.focus()

    def on_save():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        _save_credentials(username, password)

        messagebox.showinfo(
            "Saved",
            "Credentials updated. The assistant will retry shortly."
        )

        window.destroy()

    def on_cancel():
        window.destroy()

    button_frame = tk.Frame(window)
    button_frame.pack(pady=15)

    tk.Button(button_frame, text="Save", command=on_save, width=10).pack(
        side="left", padx=5
    )
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(
        side="left", padx=5
    )

    window.mainloop()
