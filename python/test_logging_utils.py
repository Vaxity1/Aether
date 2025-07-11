"""
test_logging_utils.py - Unit tests for logging_utils.py
"""
import unittest
from logging_utils import setup_logging
import logging

class TestLoggingUtils(unittest.TestCase):
    def test_setup_logging_returns_logger(self):
        logger = setup_logging('test_log.log')
        self.assertIsInstance(logger, logging.Logger)
        logger.info('Test log message')

if __name__ == "__main__":
    unittest.main()
