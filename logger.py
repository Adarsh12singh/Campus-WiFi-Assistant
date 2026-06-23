from datetime import datetime
import os

def write_log(message):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "logs.txt"
        )

        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"[{current_time}] {message}\n")

    except Exception as e:
        print(f"Log Error: {e}")
