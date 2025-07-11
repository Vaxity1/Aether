# Execute before delivery:
python -m py_compile *.py          # Syntax check
python -m flake8 .                 # Style check
python -m mypy .                   # Type check
python -m pytest -v               # Run tests
python -m coverage run -m pytest  # Coverage analysis
