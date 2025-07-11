"""
error_trend_report.py - Visualize error trends and solution suggestions
Generates a markdown report of error frequencies and solution hints.
"""
import os
import json
from datetime import datetime

PATTERNS_PATH = os.path.join(os.path.dirname(__file__), '..', 'error_patterns.json')
REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'error_trend_report.md')

def generate_report():
    if not os.path.exists(PATTERNS_PATH):
        print('[ErrorTrendReport] No error_patterns.json found.')
        return
    with open(PATTERNS_PATH, 'r', encoding='utf-8') as f:
        patterns = json.load(f)
    lines = [f"# Error Trend Report\n\nGenerated: {datetime.now().isoformat()}\n"]
    lines.append('| Error Type | Frequency | Last Seen | Solution Suggestion |')
    lines.append('|------------|-----------|-----------|--------------------|')
    for key, val in patterns.get('error_patterns', {}).items():
        freq = val.get('frequency', 0)
        last_seen = val.get('last_seen', '-')
        solution = val.get('solution_hint', '-')
        lines.append(f"| {key} | {freq} | {last_seen} | {solution} |")
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[ErrorTrendReport] Report generated at {REPORT_PATH}')

if __name__ == "__main__":
    generate_report()
