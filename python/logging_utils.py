"""
logging_utils.py - Logging Setup and Utilities
Configures logging for the hybrid workflow system.
"""
import logging

def setup_logging(logfile: str = 'python_workflow.log') -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(logfile, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('PythonWorkflow')
    return logger
