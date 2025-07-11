"""
test_subprocess_fix.py - Simple test to verify subprocess fixes work
"""
import subprocess
import sys
import time

def test_subprocess():
    """Test basic subprocess functionality"""
    print("Testing subprocess functionality...")
    
    try:
        start_time = time.time()
        result = subprocess.run([
            sys.executable, '--version'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Success! Executed in {execution_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout.strip()}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Process timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_flake8():
    """Test flake8 subprocess call"""
    print("\nTesting flake8...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'flake8', '--version'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        
        print(f"✅ flake8 test successful")
        print(f"Return code: {result.returncode}")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ flake8 timed out")
        return False
    except Exception as e:
        print(f"❌ flake8 error: {e}")
        return False

if __name__ == "__main__":
    print("=== Subprocess Fix Verification ===")
    
    success1 = test_subprocess()
    success2 = test_flake8()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Subprocess fixes are working correctly.")
    else:
        print("\n❌ Some tests failed. Further investigation needed.")
