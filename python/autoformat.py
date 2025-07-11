"""
autoformat.py - Automated code formatting and cleanup
Formats all Python files in the target codebase using black and autoflake.
"""
import subprocess
import os
import json
import sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def autoformat_codebase():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    codebase = config.get('qa_codebase', 'main.py')
    codebase_path = os.path.join(os.path.dirname(__file__), codebase)
    # Format with black and autoflake using python -m for compatibility
    if os.path.isdir(codebase_path):
        subprocess.run([sys.executable, '-m', 'black', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
        subprocess.run([sys.executable, '-m', 'autoflake', '--in-place', '--remove-unused-variables', '--remove-all-unused-imports', '--recursive', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
    else:
        subprocess.run([sys.executable, '-m', 'black', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
        subprocess.run([sys.executable, '-m', 'autoflake', '--in-place', '--remove-unused-variables', '--remove-all-unused-imports', codebase_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=False)
    print(f"[Autoformat] Formatted {codebase_path} with black and autoflake.")

if __name__ == "__main__":
    autoformat_codebase()
