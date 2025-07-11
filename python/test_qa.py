"""
test_qa.py - Unit tests for qa.py (Quality Assurance)
"""
from qa import run_quality_assurance
import unittest
import os

class TestQualityAssurance(unittest.TestCase):
    def test_run_quality_assurance(self):
        codebase = os.path.dirname(__file__)
        results = run_quality_assurance(codebase)
        self.assertIn('flake8_passed', results)
        self.assertIn('mypy_passed', results)
        self.assertIn('pytest_passed', results)
        self.assertIsInstance(results['flake8_passed'], bool)
        self.assertIsInstance(results['mypy_passed'], bool)
        self.assertIsInstance(results['pytest_passed'], bool)

if __name__ == "__main__":
    unittest.main()
