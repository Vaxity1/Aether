from typing import Any, Dict, List
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
from logging_utils import setup_logging
from workflow import HybridWorkflow
from qa import run_quality_assurance
from task_manager import TaskManagerModule
from session import write_session_summary, log_session_event
from error_patterns import recognize_error_patterns

def is_running_under_pytest():
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

logger = setup_logging(config.get('logfile', 'python_workflow.log'))

if __name__ == "__main__":
    if is_running_under_pytest():
        print("[Orchestrator] Detected pytest environment, exiting to prevent recursion.")
        sys.exit(0)
    context: Dict[str, Any] = config.get('default_context', {})
    tasks: List[Dict[str, Any]] = [
        {'name': 'Implement feature X', 'importance': 3, 'urgency': 2, 'introduces_new_pattern': True},
        {'name': 'Fix bug Y', 'importance': 2, 'urgency': 3, 'introduces_new_pattern': False}
    ]
    error_patterns: Dict[str, Any] = {
        'syntax_errors': {},
        'logic_errors': {}
    }
    workflow = HybridWorkflow(context, tasks, error_patterns)
    workflow.run_full_workflow()
    qa_results = run_quality_assurance(config.get('qa_codebase', 'my_codebase'))
    log_session_event('QA Results', qa_results, logger)
    write_session_summary(context, workflow.accomplishments, workflow.metrics, workflow.learning, logger)
    logger.info('Main execution completed successfully.')
