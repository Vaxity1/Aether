"""
error_pattern_learn.py - Automated error pattern learning and update
Scans recent logs for new error patterns and updates error_patterns.json.
"""
import os
import json
import re
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'session_log.txt')
PATTERNS_PATH = os.path.join(os.path.dirname(__file__), '..', 'error_patterns.json')

# Simple regexes for error types (extend as needed)
ERROR_REGEXES = {
    'syntax_errors': re.compile(r'SyntaxError|IndentationError|TabError'),
    'logic_errors': re.compile(r'AssertionError|ValueError|TypeError|KeyError'),
    'import_errors': re.compile(r'ImportError|ModuleNotFoundError'),
    'file_errors': re.compile(r'FileNotFoundError|IOError|OSError'),
    'runtime_errors': re.compile(r'RuntimeError|Exception'),
}

# Solution suggestions for error types
SOLUTION_HINTS = {
    'syntax_errors': 'Check for missing colons, parentheses, or indentation. Use a linter for syntax validation.',
    'logic_errors': 'Add or improve unit tests for edge cases. Use assertions and debug step-by-step.',
    'import_errors': 'Verify module/package names and installation. Check your PYTHONPATH and venv.',
    'file_errors': 'Check file paths, permissions, and existence before accessing files.',
    'runtime_errors': 'Add try/except blocks and log exceptions. Review stack traces for root causes.'
}

def learn_error_patterns():
    # Load existing patterns
    if os.path.exists(PATTERNS_PATH):
        with open(PATTERNS_PATH, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
    else:
        patterns = {'error_patterns': {}, 'solution_database': {}, 'learning_metrics': {}}
    # Scan recent logs
    if not os.path.exists(LOG_PATH):
        print('[ErrorPatternLearn] No session_log.txt found.')
        return
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-200:]
    found = set()
    for line in lines:
        for key, regex in ERROR_REGEXES.items():
            if regex.search(line):
                found.add(key)
    # Update error_patterns.json
    updated = False
    for key in found:
        if key not in patterns['error_patterns']:
            patterns['error_patterns'][key] = {
                'frequency': 1,
                'last_seen': datetime.now().isoformat(),
                'solution_hint': SOLUTION_HINTS.get(key, 'No suggestion available.')
            }
            updated = True
        else:
            patterns['error_patterns'][key]['frequency'] = patterns['error_patterns'][key].get('frequency', 0) + 1
            patterns['error_patterns'][key]['last_seen'] = datetime.now().isoformat()
            if 'solution_hint' not in patterns['error_patterns'][key]:
                patterns['error_patterns'][key]['solution_hint'] = SOLUTION_HINTS.get(key, 'No suggestion available.')
            updated = True
    if updated:
        with open(PATTERNS_PATH, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        print('[ErrorPatternLearn] Updated error_patterns.json with new patterns.')
    else:
        print('[ErrorPatternLearn] No new error patterns found.')

if __name__ == "__main__":
    learn_error_patterns()
