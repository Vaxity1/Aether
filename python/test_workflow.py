"""
test_workflow.py - Unit tests for workflow.py and related modules
"""
import unittest
from workflow import HybridWorkflow
from typing import Any, Dict, List

class TestHybridWorkflow(unittest.TestCase):
    def setUp(self):
        self.context: Dict[str, Any] = {
            'project_complexity': 'intermediate',
            'development_phase': 'implementation',
            'error_rate': 0.05,
            'technical_debt': 0.2
        }
        self.tasks: List[Dict[str, Any]] = [
            {'name': 'Test feature', 'importance': 2, 'urgency': 2, 'introduces_new_pattern': False}
        ]
        self.error_patterns: Dict[str, Any] = {
            'syntax_errors': {},
            'logic_errors': {}
        }
        self.workflow = HybridWorkflow(self.context, self.tasks, self.error_patterns)

    def test_workflow_phases(self):
        log = self.workflow.run_full_workflow()
        self.assertIn('Session initialized with context analysis.', log)
        self.assertIn('Error analysis and resolution complete.', log)
        self.assertIn('Strategic refactoring and validation complete.', log)
        self.assertIn('User requests fulfilled and validated.', log)
        self.assertIn('Final optimization and learning logged.', log)
        self.assertTrue('feature_count' in self.workflow.accomplishments)

    def test_feature_count(self):
        self.workflow.phase4_dynamic_feature_development()
        self.assertGreaterEqual(self.workflow.accomplishments['feature_count'], 1)
        self.assertLessEqual(self.workflow.accomplishments['feature_count'], 5)

if __name__ == "__main__":
    unittest.main()
