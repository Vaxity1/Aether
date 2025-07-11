"""
session.py - Session Management and Logging
Handles session summary writing and event logging.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional
import logging

def write_session_summary(context: Dict[str, Any], accomplishments: Dict[str, Any], metrics: Dict[str, Any], learning: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
    timestamp = datetime.now().isoformat()
    summary = f"""## Session Summary - {timestamp}

### Context Analysis
- Project Phase: {context.get('development_phase', 'N/A')}
- Complexity Level: {context.get('complexity_level', 'N/A')}
- Error Rate: {metrics.get('error_rate', 'N/A')}
- Technical Debt: {context.get('technical_debt', 'N/A')}

### Adaptive Decisions
- Feature Count: {accomplishments.get('feature_count', 'N/A')}
- Priority Focus: {accomplishments.get('priority_focus', 'N/A')}
- Quality Gates: {accomplishments.get('quality_gates', 'N/A')}

### Accomplishments
- Errors Resolved: {accomplishments.get('errors_resolved', 'N/A')}
- Features Implemented: {accomplishments.get('features_implemented', 'N/A')}
- Refactoring Completed: {accomplishments.get('refactoring_completed', 'N/A')}
- Tests Added: {accomplishments.get('tests_added', 'N/A')}

### Learning Outcomes
- New Error Patterns: {learning.get('new_error_patterns', 'N/A')}
- Performance Improvements: {learning.get('performance_improvements', 'N/A')}
- Code Quality Enhancements: {learning.get('code_quality_enhancements', 'N/A')}
- User Experience Gains: {learning.get('user_experience_gains', 'N/A')}

### Next Session Preparation
- Priority Tasks: {learning.get('priority_tasks', 'N/A')}
- Technical Debt Items: {learning.get('technical_debt_items', 'N/A')}
- Performance Targets: {learning.get('performance_targets', 'N/A')}
- Learning Focus: {learning.get('learning_focus', 'N/A')}

### Metrics
- Session Duration: {metrics.get('session_duration', 'N/A')}
- Feature Velocity: {metrics.get('feature_velocity', 'N/A')}
- Error Resolution Rate: {metrics.get('error_resolution_rate', 'N/A')}
- Code Quality Score: {metrics.get('code_quality_score', 'N/A')}
- User Satisfaction: {metrics.get('user_satisfaction', 'N/A')}
"""
    try:
        with open("session_summary.log", "a", encoding="utf-8") as f:
            f.write(summary + "\n\n")
        if logger:
            logger.info("Session summary written successfully.")
    except Exception as e:
        if logger:
            logger.error(f"Failed to write session summary: {e}")

def log_session_event(event: str, details: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None) -> None:
    timestamp = datetime.now().isoformat()
    with open('session_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {event}: {json.dumps(details or {})}\n")
    if logger:
        logger.info(f"Session event logged: {event}")
