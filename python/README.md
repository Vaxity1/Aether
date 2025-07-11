# Hybrid AI Copilot Python Workflow System

This directory contains a modular, production-ready workflow/orchestration system for hybrid AI copilot development. It is designed for extensibility, robust error handling, real QA/test integration, and configuration-driven operation.

## Structure

- `python.py` — Main entry point, integrates all modules and loads configuration.
- `config.json` — Central configuration for paths, context, and QA settings.
- `workflow.py` — Implements the 6-phase hybrid workflow process.
- `qa.py` — Quality assurance and test integration (flake8, mypy, pytest).
- `task_manager.py` — Task prioritization and execution logic.
- `logging_utils.py` — Logging setup and utilities.
- `session.py` — Session summary writing and event logging.
- `error_patterns.py` — Error pattern recognition system.

## Usage

1. **Configure**: Edit `config.json` to set paths, context, and QA targets.
2. **Run**: Execute `python python.py` from this directory.
3. **Extend**: Add new workflow phases, QA steps, or task types by creating new modules and importing them in `python.py`.

## Extensibility
- All modules are designed for easy extension and replacement.
- Add new workflow phases by subclassing or extending `HybridWorkflow`.
- Plug in new QA tools by extending `qa.py`.
- Add new error pattern logic in `error_patterns.py`.

## Configuration
- All file paths, context, and QA settings are managed in `config.json`.
- No hardcoded values in code—edit config to change behavior.

## Quality Assurance
- Runs `flake8`, `mypy`, and `pytest` on the codebase specified in config.
- Logs all results and errors to the logfile set in config.

## Logging
- All major events and errors are logged to both file and console.
- Logfile path is set in `config.json`.

## Session Management
- Session summaries and logs are written to files specified in config.
- Use `write_session_summary` and `log_session_event` for structured logging.

## Example

```
python python.py
```

## Requirements
- Python 3.8+
- `flake8`, `mypy`, `pytest` installed in your environment

## License
MIT
