from datetime import datetime
import os

from app_paths import get_app_dir


def write_log(message):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_path = os.path.join(get_app_dir(), "logs.txt")

        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"[{current_time}] {message}\n")

    except Exception as e:
        print(f"Log Error: {e}")
