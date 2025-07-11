"""
backup_and_heal.py - Automated backup and rollback/healing for workflow automation
"""
import os
import shutil
import json
import datetime
import subprocess
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups', 'auto')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'backup_heal.log')

os.makedirs(BACKUP_DIR, exist_ok=True)

def log_event(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def backup_file(filepath):
    if not os.path.exists(filepath):
        return None
    base = os.path.basename(filepath)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f"{base}.{timestamp}.bak")
    shutil.copy2(filepath, backup_path)
    log_event(f"Backed up {filepath} to {backup_path}")
    return backup_path

def restore_file(backup_path, target_path):
    shutil.copy2(backup_path, target_path)
    log_event(f"Restored {target_path} from {backup_path}")

def run_workflow_and_check():
    # Run tests only (exclude tools directory to avoid picking up automation scripts)
    test_dir = os.path.dirname(__file__)
    test_files = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    if not test_files:
        log_event("No test files found for workflow check.")
        return True
    test_result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '--maxfail=5', '--disable-warnings', *test_files],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=300
    )
    # If tests fail, return False
    if test_result.returncode != 0:
        log_event(f"Tests failed.\nTest output:\n{test_result.stdout}\n{test_result.stderr}")
        return False
    return True

def is_running_under_pytest():
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None

def main():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    codebase = config.get('qa_codebase', 'main.py')
    codebase_path = os.path.join(os.path.dirname(__file__), codebase)
    # Backup target(s)
    backup_paths: list[tuple[str | None, str]] = []
    if os.path.isdir(codebase_path):
        for fname in os.listdir(codebase_path):
            if fname.endswith('.py'):
                backup_paths.append((backup_file(os.path.join(codebase_path, fname)), os.path.join(codebase_path, fname)))
    else:
        backup_paths.append((backup_file(codebase_path), codebase_path))
    # Run workflow and check
    if not run_workflow_and_check():
        # Restore from backup
        for bpath, tpath in backup_paths:
            if bpath is not None:
                restore_file(bpath, tpath)
        log_event("Rollback performed due to workflow/test failure.")
    else:
        log_event("Workflow and tests passed. No rollback needed.")

if __name__ == "__main__":
    if is_running_under_pytest():
        print("[Backup/Heal] Detected pytest environment, exiting to prevent recursion.")
        sys.exit(0)
    main()
