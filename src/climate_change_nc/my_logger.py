from datetime import datetime
from pathlib import Path

LOG_DIR = f"{Path.home()}/.climate_change_nc/log"


class MyLogger:
    def __init__(self, date):
        self.logfile = f"{LOG_DIR}/{date.strftime('%y%m%d')}.log"

        Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.logfile).touch(exist_ok=True)

    def log(self, msg):
        log_msg = f"[{datetime.now().strftime('%y%m%d-%H%M%S')}] {msg}"
        with open(self.logfile, 'a') as logfile:
            logfile.write(f"{log_msg}\n")

        print(log_msg)

    def error(self, msg):
        self.log(f"[ERROR] {msg}")
