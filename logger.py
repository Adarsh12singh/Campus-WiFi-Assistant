from datetime import datetime

def write_log(message):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs.txt", "a", encoding="utf-8") as file:
        file.write(f"[{current_time}] {message}\n")