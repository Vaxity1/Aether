"""
test_integration.py - Integration test for end-to-end workflow execution
"""
import unittest
import os
import sys
from typing import Any, Dict, List
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
from workflow import HybridWorkflow
from qa import run_quality_assurance

class TestIntegrationWorkflow(unittest.TestCase):
    def setUp(self):
        self.context: Dict[str, Any] = {
            'project_complexity': 'intermediate',
            'development_phase': 'implementation',
            'error_rate': 0.05,
            'technical_debt': 0.2
        }
        self.tasks: List[Dict[str, Any]] = [
            {'name': 'Integration feature', 'importance': 2, 'urgency': 2, 'introduces_new_pattern': False}
        ]
        self.error_patterns: Dict[str, Any] = {
            'syntax_errors': {},
            'logic_errors': {}
        }

    def test_full_workflow_and_qa(self):
        workflow = HybridWorkflow(self.context, self.tasks, self.error_patterns)
        log = workflow.run_full_workflow()
        self.assertIn('Session initialized with context analysis.', log)
        self.assertIn('Final optimization and learning logged.', log)
        qa_results = run_quality_assurance(os.path.dirname(__file__))
        self.assertIn('flake8_passed', qa_results)
        self.assertIn('mypy_passed', qa_results)
        self.assertIn('pytest_passed', qa_results)
        self.assertIsInstance(qa_results['flake8_passed'], bool)
        self.assertIsInstance(qa_results['mypy_passed'], bool)
        self.assertIsInstance(qa_results['pytest_passed'], bool)

if __name__ == "__main__":
    unittest.main()
