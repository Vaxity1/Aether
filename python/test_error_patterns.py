"""
test_error_patterns.py - Unit tests for error_patterns.py
"""
import unittest
from error_patterns import recognize_error_patterns

class TestErrorPatterns(unittest.TestCase):
    def test_recognize_error_patterns(self):
        logs = [
            "syntax_errors: missing semicolon",
            "logic_errors: edge case"
        ]
        error_patterns = {
            'syntax_errors': {},
            'logic_errors': {}
        }
        recognized = recognize_error_patterns(logs, error_patterns)
        self.assertIn('syntax_errors', recognized)
        self.assertIn('logic_errors', recognized)
        self.assertEqual(len(recognized), 2)

if __name__ == "__main__":
    unittest.main()
