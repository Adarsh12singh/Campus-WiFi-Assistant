import sys
import os


def get_app_dir():
    """
    Returns the folder where persistent, user-editable files
    (config.json, logs.txt) should live.

    - When running as a normal .py script: the project root folder.
    - When running as a packaged .exe (PyInstaller): the folder
      containing the .exe itself, NOT the temporary _MEIPASS
      extraction folder that PyInstaller unpacks bundled code into.
      Using __file__ here would silently point into that temp folder,
      which is wiped after the app closes - so config/logs would
      never actually persist.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    """
    Returns the folder to load bundled, read-only resources from
    (e.g. campus_wifi.png for the tray icon).

    - When running as a normal .py script: the project root folder.
    - When running as a packaged .exe: PyInstaller's temporary
      _MEIPASS extraction folder, where files listed in the spec's
      `datas` actually get unpacked to at runtime. This is DIFFERENT
      from get_app_dir() - resources bundled into the exe live here,
      not next to the exe file.
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", get_app_dir())

    return os.path.dirname(os.path.abspath(__file__))
