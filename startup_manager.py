import os
import shutil

def add_to_startup():

    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    current_file = os.path.abspath("CampusWiFiAssistant.bat")

    destination = os.path.join(
        startup_folder,
        "CampusWiFiAssistant.bat"
    )

    shutil.copy(current_file, destination)

    print("Added To Startup")