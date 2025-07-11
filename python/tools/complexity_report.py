"""
Automated Code Complexity and Maintainability Analysis
- Uses radon to analyze code complexity and maintainability
- Generates a markdown report with visualizations/trends
"""
import subprocess
import sys

def analyze_complexity(output_file: str = "complexity_trend.md"):
    """Analyze code complexity and write report."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Code Complexity and Maintainability Report\n\n")
        # Cyclomatic complexity
        f.write("## Cyclomatic Complexity (radon cc)\n\n")
        cc = subprocess.run([sys.executable, "-m", "radon", "cc", "..", "-s", "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, capture_output=True, text=True)
        f.write("```")
        f.write(cc.stdout)
        f.write("```)\n\n")
        # Maintainability index
        f.write("## Maintainability Index (radon mi)\n\n")
        mi = subprocess.run([sys.executable, "-m", "radon", "mi", ".."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, capture_output=True, text=True)
        f.write("```")
        f.write(mi.stdout)
        f.write("```)\n\n")
    print(f"Complexity report written to {output_file}")

if __name__ == "__main__":
    analyze_complexity()
