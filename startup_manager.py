import os
import sys

from app_paths import get_app_dir

SHORTCUT_NAME = "CampusWiFiAssistant.bat"


def _get_startup_folder():
    return os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )


def _get_launch_command():
    """
    Builds the command to run on Windows startup.
    - Packaged exe: launches the exe directly.
    - Dev/script mode: launches main.py with whichever Python
      interpreter is currently running this process (sys.executable),
      instead of a hardcoded path that would break on another machine.
    """
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    main_py = os.path.join(get_app_dir(), "main.py")
    return f'"{sys.executable}" "{main_py}"'


def add_to_startup():
    os.makedirs(_get_startup_folder(), exist_ok=True)

    destination = os.path.join(_get_startup_folder(), SHORTCUT_NAME)
    launch_command = _get_launch_command()

    with open(destination, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("REM Wait for the drive to finish mounting after boot\n")
        f.write("timeout /t 15 /nobreak >nul\n")
        f.write(f'cd /d "{get_app_dir()}"\n')
        f.write(f"start \"\" {launch_command}\n")

    print("Added To Startup")


def remove_from_startup():
    destination = os.path.join(_get_startup_folder(), SHORTCUT_NAME)

    if os.path.exists(destination):
        os.remove(destination)
        print("Removed From Startup")


def is_in_startup():
    destination = os.path.join(_get_startup_folder(), SHORTCUT_NAME)
    return os.path.exists(destination)
