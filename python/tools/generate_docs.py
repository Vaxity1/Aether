"""
Automated Documentation Generation and Validation
- Generates HTML/Markdown docs for all modules using pdoc
- Validates docstring coverage and style
- Notifies or fails workflow if coverage drops below threshold
"""
import subprocess
import sys

def generate_docs(output_dir: str = "docs"):
    """Generate documentation using pdoc."""
    subprocess.run([sys.executable, "-m", "pdoc", "--output-dir", output_dir, "--force", ".."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, check=True)
    print(f"Documentation generated in {output_dir}/")

def validate_docstrings(threshold: float = 0.8):
    """Validate docstring coverage using docstr-coverage and fail if below threshold."""
    try:
        result = subprocess.run([sys.executable, "-m", "docstr_coverage", ".."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, capture_output=True, text=True)
        print(result.stdout)
        for line in result.stdout.splitlines():
            if "Docstring coverage:" in line:
                percent = float(line.split(":")[-1].strip().replace("%", "")) / 100
                if percent < threshold:
                    print(f"Docstring coverage {percent*100:.1f}% below threshold {threshold*100:.1f}%")
                    sys.exit(1)
                else:
                    print(f"Docstring coverage OK: {percent*100:.1f}%")
    except Exception as e:
        print(f"Docstring validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_docs()
    validate_docstrings()
