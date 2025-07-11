import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_FILE = "main.py"
SCRIPT_TO_RUN = ".pre-commit-all-in-one.py"

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(WATCHED_FILE):
            print(f"{WATCHED_FILE} changed, running backup/QA script...")
            subprocess.run(["python", SCRIPT_TO_RUN])

if __name__ == "__main__":
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    print(f"Watching {WATCHED_FILE} for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()