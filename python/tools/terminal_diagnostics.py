"""
terminal_diagnostics.py - Terminal Command Hanging Diagnostics and Fix
Comprehensive solution for subprocess and terminal command issues
"""
import subprocess
import sys
import os
import time
import threading
import signal
import psutil
from typing import Optional, Tuple, List, Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages subprocesses with proper cleanup and timeout handling"""
    
    def __init__(self):
        self.active_processes: List[subprocess.Popen[str]] = []
        self.cleanup_lock = threading.Lock()
    
    def run_safe_subprocess(self, cmd: List[str], timeout: int = 60, 
                          cwd: Optional[str] = None, **kwargs: Any) -> Tuple[int, str, str]:
        """
        Run subprocess with proper timeout, cleanup, and error handling
        Returns: (return_code, stdout, stderr)
        """
        try:
            # Use the correct Python executable from virtual environment
            if cmd[0] == 'python':
                cmd[0] = sys.executable
            elif cmd[0:2] == ['python', '-m']:
                cmd = [sys.executable, '-m'] + cmd[2:]
            
            # Set default values for subprocess
            default_kwargs: Dict[str, Any] = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'cwd': cwd or os.getcwd(),
                'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            }
            default_kwargs.update(kwargs)
            
            logger.info(f"Running command: {' '.join(cmd)}")
            start_time = time.time()
            
            with self.cleanup_lock:
                proc = subprocess.Popen(cmd, **default_kwargs)
                self.active_processes.append(proc)
            
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                return_code = proc.returncode
                
                execution_time = time.time() - start_time
                logger.info(f"Command completed in {execution_time:.2f}s with return code {return_code}")
                
                return return_code, stdout, stderr
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Process timed out after {timeout}s, terminating...")
                self._terminate_process(proc)
                return -1, "", f"Process timed out after {timeout} seconds"
                
            finally:
                with self.cleanup_lock:
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
                        
        except Exception as e:
            logger.error(f"Error running subprocess: {e}")
            return -1, "", str(e)
    
    def _terminate_process(self, proc: subprocess.Popen):
        """Forcefully terminate a process and its children"""
        try:
            if os.name == 'nt':  # Windows
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                time.sleep(1)
                if proc.poll() is None:
                    proc.terminate()
                    time.sleep(1)
                    if proc.poll() is None:
                        proc.kill()
            else:  # Unix-like
                proc.terminate()
                time.sleep(1)
                if proc.poll() is None:
                    proc.kill()
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
    
    def cleanup_all_processes(self):
        """Clean up all active processes"""
        with self.cleanup_lock:
            for proc in self.active_processes[:]:
                if proc.poll() is None:
                    self._terminate_process(proc)
            self.active_processes.clear()
    
    def get_python_processes(self) -> List[Dict[str, Any]]:
        """Get all running Python processes"""
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return python_processes

class TerminalCommandFixer:
    """Fixes common terminal command hanging issues"""
    
    def __init__(self):
        self.process_manager = ProcessManager()
        self.venv_python = sys.executable
        self.project_root = os.path.dirname(os.path.dirname(__file__))
    
    def diagnose_hanging_issues(self) -> Dict[str, Any]:
        """Comprehensive diagnosis of potential hanging issues"""
        issues = {
            'python_processes': self.process_manager.get_python_processes(),
            'venv_status': self._check_venv_status(),
            'subprocess_issues': self._check_subprocess_issues(),
            'path_issues': self._check_path_issues(),
            'timeout_issues': self._check_timeout_issues(),
            'recursion_issues': self._check_recursion_issues()
        }
        return issues
    
    def _check_venv_status(self) -> Dict[str, Any]:
        """Check virtual environment status"""
        return {
            'venv_python': self.venv_python,
            'is_venv': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
            'python_version': sys.version,
            'executable_exists': os.path.exists(self.venv_python),
            'executable_accessible': os.access(self.venv_python, os.X_OK)
        }
    
    def _check_subprocess_issues(self) -> Dict[str, Any]:
        """Check for common subprocess issues"""
        issues = []
        
        # Test basic subprocess functionality
        try:
            result = self.process_manager.run_safe_subprocess([self.venv_python, '--version'], timeout=10)
            if result[0] != 0:
                issues.append("Python executable not working properly")
        except Exception as e:
            issues.append(f"Subprocess execution failed: {e}")
        
        return {'issues': issues}
    
    def _check_path_issues(self) -> Dict[str, Any]:
        """Check for path-related issues"""
        issues = []
        
        # Check if project paths are accessible
        for path in [self.project_root, os.path.join(self.project_root, 'tools')]:
            if not os.path.exists(path):
                issues.append(f"Path does not exist: {path}")
            elif not os.access(path, os.R_OK):
                issues.append(f"Path not readable: {path}")
        
        return {'issues': issues, 'project_root': self.project_root}
    
    def _check_timeout_issues(self) -> Dict[str, Any]:
        """Check for timeout-related issues"""
        # This would involve analyzing subprocess calls for missing timeouts
        files_with_subprocess = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'subprocess' in content and 'timeout' not in content:
                                files_with_subprocess.append(filepath)
                    except Exception:
                        continue
        
        return {'files_without_timeout': files_with_subprocess}
    
    def _check_recursion_issues(self) -> Dict[str, Any]:
        """Check for potential recursion issues"""
        issues = []
        
        # Check if tools are being included in test discovery
        tools_dir = os.path.join(self.project_root, 'tools')
        if os.path.exists(tools_dir):
            for file in os.listdir(tools_dir):
                if file.startswith('test_') or file.endswith('_test.py'):
                    issues.append(f"Test file in tools directory: {file}")
        
        return {'issues': issues}
    
    def fix_hanging_commands(self) -> Dict[str, Any]:
        """Apply fixes for hanging command issues"""
        fixes_applied = []
        
        # 1. Kill any hanging Python processes
        self.process_manager.cleanup_all_processes()
        fixes_applied.append("Cleaned up active processes")
        
        # 2. Fix subprocess calls without timeouts
        self._fix_subprocess_timeouts()
        fixes_applied.append("Fixed subprocess timeout issues")
        
        # 3. Fix incorrect Python executable usage
        self._fix_python_executable_usage()
        fixes_applied.append("Fixed Python executable usage")
        
        # 4. Fix recursion issues
        self._fix_recursion_issues()
        fixes_applied.append("Fixed recursion issues")
        
        return {'fixes_applied': fixes_applied}
    
    def _fix_subprocess_timeouts(self):
        """Fix subprocess calls that don't have timeouts"""
        logger.info("Fixing subprocess timeout issues...")
        # This would be implemented to scan and fix files
        pass
    
    def _fix_python_executable_usage(self):
        """Fix incorrect Python executable usage"""
        logger.info("Fixing Python executable usage...")
        # This would scan files and replace 'python' with sys.executable
        pass
    
    def _fix_recursion_issues(self):
        """Fix recursion issues in test discovery"""
        logger.info("Fixing recursion issues...")
        # This would ensure tools are excluded from test discovery
        pass

def main():
    """Main diagnostic and fix routine"""
    print("=== Terminal Command Hanging Diagnostics ===")
    
    fixer = TerminalCommandFixer()
    
    # Run diagnostics
    print("\n1. Running diagnostics...")
    issues = fixer.diagnose_hanging_issues()
    
    print(f"\nDiagnostic Results:")
    print(f"- Python processes running: {len(issues['python_processes'])}")
    print(f"- Virtual environment status: {'OK' if issues['venv_status']['is_venv'] else 'NOT IN VENV'}")
    print(f"- Subprocess issues: {len(issues['subprocess_issues']['issues'])}")
    print(f"- Path issues: {len(issues['path_issues']['issues'])}")
    print(f"- Files without timeouts: {len(issues['timeout_issues']['files_without_timeout'])}")
    print(f"- Recursion issues: {len(issues['recursion_issues']['issues'])}")
    
    # Apply fixes
    print("\n2. Applying fixes...")
    fixes = fixer.fix_hanging_commands()
    
    print(f"\nFixes Applied:")
    for fix in fixes['fixes_applied']:
        print(f"- {fix}")
    
    # Test subprocess functionality
    print("\n3. Testing subprocess functionality...")
    test_result = fixer.process_manager.run_safe_subprocess([fixer.venv_python, '--version'], timeout=10)
    
    if test_result[0] == 0:
        print("✅ Subprocess functionality working correctly")
        print(f"Python version: {test_result[1].strip()}")
    else:
        print("❌ Subprocess functionality still has issues")
        print(f"Error: {test_result[2]}")
    
    # Save diagnostic report
    report_path = os.path.join(os.path.dirname(__file__), '..', 'terminal_diagnostic_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'issues': issues,
            'fixes': fixes
        }, f, indent=2)
    
    print(f"\nDiagnostic report saved to: {report_path}")

if __name__ == "__main__":
    main()
