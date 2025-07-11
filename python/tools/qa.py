"""
qa.py - Quality Assurance and Testing Module
Handles code quality checks and test integration using real tools.
"""
import subprocess
import sys
import os
from typing import Any, Dict

def run_quality_assurance(codebase: str) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    base_dir = os.path.abspath(codebase)
    
    # Run flake8
    try:
        flake8_proc = subprocess.run([
            sys.executable, '-m', 'flake8', base_dir
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        results['flake8_passed'] = flake8_proc.returncode == 0
        results['flake8_output'] = flake8_proc.stdout + flake8_proc.stderr
    except subprocess.TimeoutExpired:
        results['flake8_passed'] = False
        results['flake8_output'] = "flake8 timed out"
    except Exception as e:
        results['flake8_passed'] = False
        results['flake8_output'] = f"Exception: {e}"
    
    # Run mypy
    try:
        mypy_proc = subprocess.run([
            sys.executable, '-m', 'mypy', base_dir
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        results['mypy_passed'] = mypy_proc.returncode == 0
        results['mypy_output'] = mypy_proc.stdout + mypy_proc.stderr
    except subprocess.TimeoutExpired:
        results['mypy_passed'] = False
        results['mypy_output'] = "mypy timed out"
    except Exception as e:
        results['mypy_passed'] = False
        results['mypy_output'] = f"Exception: {e}"
    
    # Run pytest
    try:
        pytest_proc = subprocess.run([
            sys.executable, '-m', 'pytest', base_dir, '--maxfail=5', '--disable-warnings', '-q',
            '--ignore=tools/'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        results['pytest_passed'] = pytest_proc.returncode == 0
        results['pytest_output'] = pytest_proc.stdout + pytest_proc.stderr
    except subprocess.TimeoutExpired:
        results['pytest_passed'] = False
        results['pytest_output'] = "pytest timed out"
    except Exception as e:
        results['pytest_passed'] = False
        results['pytest_output'] = f"Exception: {e}"
    
    # Summary
    results['syntax_validation'] = results.get('flake8_passed', False)
    results['style_compliance'] = results.get('flake8_passed', False)
    results['type_checking'] = results.get('mypy_passed', False)
    results['unit_tests'] = results.get('pytest_passed', False)
    results['all_passed'] = all([
        results['flake8_passed'],
        results['mypy_passed'],
        results['pytest_passed']
    ])
    
    return results
