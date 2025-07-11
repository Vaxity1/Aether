"""
subprocess_fixer.py - Automated fix for subprocess hanging issues
Scans and fixes all subprocess calls in the project
"""
import os
import re
import sys
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubprocessFixer:
    """Fixes subprocess calls to prevent hanging"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.venv_python = sys.executable
        self.fixes_applied = []
    
    def scan_and_fix_all_files(self) -> Dict[str, List[str]]:
        """Scan all Python files and fix subprocess issues"""
        results: Dict[str, List[str]] = {
            'files_fixed': [],
            'issues_found': [],
            'fixes_applied': []
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    fixed = self.fix_subprocess_in_file(filepath)
                    if fixed:
                        results['files_fixed'].append(filepath)
                        results['fixes_applied'].extend(fixed)
        
        return results
    
    def fix_subprocess_in_file(self, filepath: str) -> List[str]:
        """Fix subprocess calls in a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes: List[str] = []
            
            # Fix 1: Replace 'python' with sys.executable in subprocess calls
            content, python_fixes = self._fix_python_executable(content)
            fixes.extend(python_fixes)
            
            # Fix 2: Add timeouts to subprocess calls
            content, timeout_fixes = self._add_timeouts(content)
            fixes.extend(timeout_fixes)
            
            # Fix 3: Add proper error handling
            content, error_fixes = self._add_error_handling(content)
            fixes.extend(error_fixes)
            
            # Write back if changes were made
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Fixed {len(fixes)} issues in {filepath}")
            
            return fixes
            
        except Exception as e:
            logger.error(f"Error fixing {filepath}: {e}")
            return []
    
    def _fix_python_executable(self, content: str) -> Tuple[str, List[str]]:
        """Replace 'python' with sys.executable in subprocess calls"""
        fixes: List[str] = []
        
        # Pattern 1: subprocess.run(['python', ...])
        pattern1 = r"subprocess\.run\(\s*\[\s*['\"]python['\"]"
        matches = re.findall(pattern1, content)
        if matches:
            content = re.sub(pattern1, "subprocess.run([sys.executable", content)
            fixes.append("Fixed subprocess.run python executable")
        
        # Pattern 2: subprocess.Popen(['python', ...])
        pattern2 = r"subprocess\.Popen\(\s*\[\s*['\"]python['\"]"
        matches = re.findall(pattern2, content)
        if matches:
            content = re.sub(pattern2, "subprocess.Popen([sys.executable", content)
            fixes.append("Fixed subprocess.Popen python executable")
        
        # Pattern 3: [sys.executable, '-m', ...] instead of ['python', '-m', ...]
        pattern3 = r"\[\s*['\"]python['\"]\s*,\s*['\"](-m)['\"]"
        matches = re.findall(pattern3, content)
        if matches:
            content = re.sub(pattern3, r"[sys.executable, '\1'", content)
            fixes.append("Fixed python -m calls")
        
        # Ensure sys import is present if we made changes
        if fixes and 'import sys' not in content:
            # Add import after other imports
            import_pattern = r'(import\s+\w+.*?\n)'
            import_match = re.search(import_pattern, content)
            if import_match:
                content = content.replace(import_match.group(0), import_match.group(0) + 'import sys\n')
            else:
                content = 'import sys\n' + content
            fixes.append("Added sys import")
        
        return content, fixes
    
    def _add_timeouts(self, content: str) -> Tuple[str, List[str]]:
        """Add timeouts to subprocess calls that don't have them"""
        fixes: List[str] = []
        
        # Pattern: subprocess.run() without timeout
        pattern = r'subprocess\.run\([^)]*\)(?![^)]*timeout)'
        matches = re.findall(pattern, content)
        for match in matches:
            if 'timeout' not in match:
                # Add timeout parameter
                new_match = match[:-1] + ', timeout=60)'
                content = content.replace(match, new_match)
                fixes.append("Added timeout to subprocess.run")
        
        return content, fixes
    
    def _add_error_handling(self, content: str) -> Tuple[str, List[str]]:
        """Add proper error handling to subprocess calls"""
        fixes: List[str] = []
        
        # Look for subprocess calls without try-except
        lines = content.split('\n')
        new_lines: List[str] = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if line contains subprocess call and isn't in try block
            if ('subprocess.run' in line or 'subprocess.Popen' in line) and line.strip():
                # Look back to see if we're already in a try block
                in_try_block = False
                for j in range(max(0, i-10), i):
                    if 'try:' in lines[j] and not any('except' in lines[k] for k in range(j, i)):
                        in_try_block = True
                        break
                
                if not in_try_block:
                    # Add try-except wrapper
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    
                    new_lines.append(f"{indent_str}try:")
                    new_lines.append(f"    {line}")
                    new_lines.append(f"{indent_str}except subprocess.TimeoutExpired:")
                    new_lines.append(f"{indent_str}    logger.warning('Subprocess timed out')")
                    new_lines.append(f"{indent_str}except Exception as e:")
                    new_lines.append(f"{indent_str}    logger.error(f'Subprocess error: {{e}}')")
                    
                    fixes.append("Added error handling to subprocess call")
                    i += 1
                    continue
            
            new_lines.append(line)
            i += 1
        
        if fixes:
            content = '\n'.join(new_lines)
            # Ensure logging import
            if 'import logging' not in content:
                content = 'import logging\n' + content
                fixes.append("Added logging import")
        
        return content, fixes

def main():
    """Main execution function"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    fixer = SubprocessFixer(project_root)
    
    print("=== Subprocess Hanging Fix Tool ===")
    print(f"Scanning project: {project_root}")
    
    results = fixer.scan_and_fix_all_files()
    
    print(f"\nResults:")
    print(f"- Files fixed: {len(results['files_fixed'])}")
    print(f"- Total fixes applied: {len(results['fixes_applied'])}")
    
    if results['files_fixed']:
        print(f"\nFixed files:")
        for file in results['files_fixed']:
            print(f"  - {file}")
    
    if results['fixes_applied']:
        print(f"\nFixes applied:")
        for fix in set(results['fixes_applied']):
            count = results['fixes_applied'].count(fix)
            print(f"  - {fix} ({count} times)")

if __name__ == "__main__":
    main()
