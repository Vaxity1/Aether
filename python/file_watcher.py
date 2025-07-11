"""
file_watcher.py - Automated file watcher to trigger workflow on changes
"""
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys
import json
import threading

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

class WorkflowTriggerHandler(FileSystemEventHandler):
    def __init__(self, targets):
        super().__init__()
        self.targets = set(os.path.abspath(t) for t in targets)
        self.last_trigger = 0
        self.cooldown = 10  # 10 second cooldown to prevent infinite loops
        self.lock = threading.Lock()

    def on_modified(self, event):
        with self.lock:
            now = time.time()
            if now - self.last_trigger < self.cooldown:
                print(f"[Watcher] Ignoring change (cooldown active): {event.src_path}")
                return
            
            if os.path.abspath(event.src_path) in self.targets:
                print(f"[Watcher] Detected change in {event.src_path}. Triggering workflow...")
                self.last_trigger = now
                
                # Run workflow steps sequentially with timeouts to prevent runaway processes
                try:
                    subprocess.run([sys.executable, 'tools/coverage_enforce.py'], 
                                 cwd=os.path.dirname(__file__), timeout=300, check=False)
                except subprocess.TimeoutExpired:
                    print("[Watcher] Coverage enforce timed out")
                except Exception as e:
                    print(f"[Watcher] Error running coverage enforce: {e}")

    def on_created(self, event):
        self.on_modified(event)

def is_running_under_pytest():
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None

if __name__ == "__main__":
    if is_running_under_pytest():
        print("[Watcher] Detected pytest environment, exiting to prevent recursion.")
        sys.exit(0)
    # Load config and determine files to watch
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    codebase = config.get('qa_codebase', 'main.py')
    if os.path.isdir(os.path.join(os.path.dirname(__file__), codebase)):
        # Watch all .py files in the directory
        targets = [os.path.join(os.path.dirname(__file__), codebase, f)
                   for f in os.listdir(os.path.join(os.path.dirname(__file__), codebase))
                   if f.endswith('.py')]
    else:
        targets = [os.path.join(os.path.dirname(__file__), codebase)]
    # Always watch config.json
    targets.append(CONFIG_PATH)
    event_handler = WorkflowTriggerHandler(targets)
    observer = Observer()
    for t in targets:
        observer.schedule(event_handler, os.path.dirname(t), recursive=False)
    print(f"[Watcher] Watching files: {targets}")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
