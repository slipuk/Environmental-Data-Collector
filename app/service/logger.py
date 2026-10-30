import pathlib
from datetime import datetime

class Logger:
    def __init__(self):
        self.path_to_log = pathlib.Path("./logs/log.log")
        self.initialize_log_file()

    def now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def initialize_log_file(self):
        self.path_to_log.parent.mkdir(parents=True, exist_ok=True)
        self.path_to_log.touch(exist_ok=True)

    def get_log_size(self):
        return self.path_to_log.stat().st_size

    def message(self, level: str, message: str):
        with open(self.path_to_log, "a", encoding="utf-8") as log:
            print(f"[{self.now()}][{level.upper()}] {message}", file=log)

log = Logger()
