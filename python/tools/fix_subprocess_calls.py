"""
fix_subprocess_calls.py - Comprehensive fix for all subprocess hanging issues
"""
import os
import re
import sys
from typing import Dict, List

def fix_file_watcher():
    """Fix the file_watcher.py subprocess call"""
    file_path = r"c:\Users\vaxit\Documents\Python2\python\file_watcher.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix subprocess call to use proper Python executable and timeout
    old_call = """subprocess.run(['python', 'tools/coverage_enforce.py'], 
                                 cwd=os.path.dirname(__file__), timeout=300, check=False)"""
    
    new_call = """subprocess.run([sys.executable, 'tools/coverage_enforce.py'], 
                                 cwd=os.path.dirname(__file__), timeout=300, check=False)"""
    
    content = content.replace(old_call, new_call)
    
    # Add sys import if not present
    if 'import sys' not in content:
        content = content.replace('import subprocess', 'import subprocess\nimport sys')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {file_path}")

def fix_qa_py():
    """Fix the qa.py subprocess calls"""
    file_path = r"c:\Users\vaxit\Documents\Python2\python\tools\qa.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all subprocess calls with proper Python executable and improved error handling
    new_content = '''"""
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
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed {file_path}")

def fix_coverage_enforce():
    """Fix the coverage_enforce.py subprocess calls"""
    file_path = r"c:\Users\vaxit\Documents\Python2\python\tools\coverage_enforce.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace subprocess calls
    content = content.replace(
        'subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest", test_dir,',
        'subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest", test_dir,'
    )
    
    # Add proper timeout and error handling
    new_content = '''"""
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
        print(f"Coverage report:\\n{output}")
        
        # Extract total coverage percentage
        for line in output.split('\\n'):
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
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed {file_path}")

def fix_all_other_files():
    """Fix subprocess calls in all other Python files"""
    files_to_fix = [
        r"c:\Users\vaxit\Documents\Python2\python\autoformat.py",
        r"c:\Users\vaxit\Documents\Python2\python\autorefactor.py",
        r"c:\Users\vaxit\Documents\Python2\python\backup_and_heal.py",
        r"c:\Users\vaxit\Documents\Python2\python\tools\generate_docs.py",
        r"c:\Users\vaxit\Documents\Python2\python\tools\complexity_report.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace subprocess.run calls to use proper format
                content = re.sub(
                    r'subprocess\.run\(\[([^]]+)\]([^)]*)\)',
                    lambda m: f'subprocess.run([{m.group(1)}], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60{m.group(2)})',
                    content
                )
                
                # Fix python executable references
                content = content.replace("'python'", "sys.executable")
                content = content.replace('"python"', "sys.executable")
                
                # Add sys import if not present
                if 'import sys' not in content and 'sys.executable' in content:
                    content = content.replace('import subprocess', 'import subprocess\\nimport sys')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed {file_path}")
                
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")

def main():
    """Main execution function"""
    print("=== Subprocess Hanging Fix Tool ===")
    print("Fixing all subprocess calls in the project...")
    
    fix_file_watcher()
    fix_qa_py()
    fix_coverage_enforce()
    fix_all_other_files()
    
    print("\\n✅ All subprocess calls have been fixed!")
    print("\\nNext steps:")
    print("1. Test the fixes by running: python tools/qa.py")
    print("2. Check file watcher: python file_watcher.py")
    print("3. Run coverage check: python tools/coverage_enforce.py")

if __name__ == "__main__":
    main()
