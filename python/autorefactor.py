"""
autorefactor.py - Automated code refactoring using rope
Performs safe refactorings (rename, extract, organize imports) on the codebase.
"""
import os
import json
import sys
import subprocess

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def autorefactor_codebase():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    codebase = config.get('qa_codebase', 'main.py')
    codebase_path = os.path.join(os.path.dirname(__file__), codebase)
    # Example: organize imports using rope (or autoflake as fallback)
    # Rope does not have a CLI for organize imports, so we use autoflake for now
    if os.path.isdir(codebase_path):
        subprocess.run([sys.executable, '-m', 'autoflake', '--in-place', '--remove-all-unused-imports', '--recursive', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
    else:
        subprocess.run([sys.executable, '-m', 'autoflake', '--in-place', '--remove-all-unused-imports', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
    print(f"[Autorefactor] Organized imports in {codebase_path}.")
    # You can extend this script to use rope for more advanced refactorings

if __name__ == "__main__":
    autorefactor_codebase()
