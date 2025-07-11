"""
coverage_enforce.py - Enforce test coverage requirements
"""
import subprocess
import sys
import os
from typing import Optional

def run_coverage_check(test_dir: str = "../", min_coverage: float = 80.0) -> bool:
    """Run coverage check and return True if meets minimum threshold"""
    try:
        # Run coverage
        result = subprocess.run([
            sys.executable, "-m", "coverage", "run", "-m", "pytest", test_dir,
            "--ignore=tools/", "--maxfail=5", "--disable-warnings", "-q"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
        
        if result.returncode != 0:
            print(f"Coverage run failed: {result.stderr}")
            return False
        
        # Get coverage report
        report_result = subprocess.run([
            sys.executable, "-m", "coverage", "report"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        
        if report_result.returncode != 0:
            print(f"Coverage report failed: {report_result.stderr}")
            return False
        
        # Parse coverage percentage
        output = report_result.stdout
        print(f"Coverage report:\n{output}")
        
        # Extract total coverage percentage
        for line in output.split('\n'):
            if 'TOTAL' in line:
                parts = line.split()
                if len(parts) >= 4:
                    coverage_str = parts[-1].replace('%', '')
                    try:
                        coverage = float(coverage_str)
                        print(f"Coverage: {coverage}% (minimum: {min_coverage}%)")
                        return coverage >= min_coverage
                    except ValueError:
                        continue
        
        return False
        
    except subprocess.TimeoutExpired:
        print("Coverage check timed out")
        return False
    except Exception as e:
        print(f"Coverage check failed: {e}")
        return False

if __name__ == "__main__":
    success = run_coverage_check()
    sys.exit(0 if success else 1)
