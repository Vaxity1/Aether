"""
error_patterns.py - Error Pattern Recognition System
Analyzes logs and matches against known error patterns.
"""
from typing import Any, Dict, List

def recognize_error_patterns(logs: List[str], error_patterns: Dict[str, Any]) -> List[str]:
    recognized: List[str] = []
    for log in logs:
        for pattern, details in error_patterns.items():
            if pattern in log:
                recognized.append(pattern)
    return recognized
