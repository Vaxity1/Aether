"""
notify.py - Automated notification/reporting for workflow automation
Sends a summary notification after workflow execution (prints to console, can be extended to email/webhook).
"""
import os
import json
import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
SESSION_SUMMARY = os.path.join(os.path.dirname(__file__), '..', 'session_summary.log')
ERROR_TREND_REPORT = os.path.join(os.path.dirname(__file__), '..', 'error_trend_report.md')


def send_notification():
    # Read last session summary
    if not os.path.exists(SESSION_SUMMARY):
        print("[Notify] No session summary found.")
        return
    with open(SESSION_SUMMARY, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Find last session summary
    last_idx = None
    for i in range(len(lines)-1, -1, -1):
        if lines[i].startswith('## Session Summary'):
            last_idx = i
            break
    if last_idx is not None:
        summary = ''.join(lines[last_idx:]).strip()
        print(f"[Notify] Last session summary:\n{summary}")
    else:
        print("[Notify] No session summary found.")

    # Print error trend summary if available
    if os.path.exists(ERROR_TREND_REPORT):
        print("\n[Notify] Error Trend Report:")
        with open(ERROR_TREND_REPORT, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("[Notify] No error trend report found.")

if __name__ == "__main__":
    send_notification()
