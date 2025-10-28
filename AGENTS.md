# Repository Guidelines

## Project Structure & Module Organization
- `mingli_mcp.py`: CLI/entrypoint (exposes `mingli-mcp`).
- `core/`: Base abstractions (systems, models, results).
- `systems/`: Pluggable fortune systems (`ziwei/`, `bazi/`, `astrology/`).
- `transports/`: IO layers (`stdio`, `http` placeholder).
- `utils/`: Validation and formatting helpers.
- `tests/`: Pytest suites for systems and transports.
- `docs/`, `examples/`, `scripts/`: Guides, config samples, utilities.

## Build, Test, and Development Commands
```bash
# Setup (recommended)
python3 -m venv venv && source venv/bin/activate
pip install -e .[dev]  # or: pip install -r requirements.txt

# Run locally
python mingli_mcp.py      # dev entry
mingli-mcp                # after editable install

# Tests and coverage
pytest -q                 # run tests
pytest --cov=. --cov-report=term-missing

# Packaging & preflight
bash scripts/check_ready_to_publish.sh
python -m build && twine check dist/*
```

## Coding Style & Naming Conventions
- Python 3.8+; PEP 8; 4-space indentation; UTF-8.
- Use type hints for public APIs; concise docstrings (first line summary).
- Naming: `snake_case` for functions/vars, `CamelCase` for classes, modules/dirs lowercase.
- Keep modules focused; new systems live under `systems/<name>/` and subclass `core.base_system.BaseFortuneSystem`.
- Avoid breaking public APIs; if necessary, update CLI, docs, and tests together.

## Testing Guidelines
- Framework: `pytest` (+ optional `pytest-cov`).
- Test files: `tests/test_*.py`; name tests by behavior, e.g. `test_bazi_element_balance`.
- Prefer fast, deterministic unit tests; use fixtures in `tests/conftest.py` if shared setup is needed.
- Cover new branches and error paths; target ≥80% coverage for changed code.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise subject. Optional prefixes used in history: `Fix:`, `Add:`, `Refactor:` (e.g., "Fix: Resolve MCP handshake issue").
- Scope in subject when helpful (e.g., `systems/bazi:`). Wrap body at ~72 chars; explain the why and notable tradeoffs.
- PRs: include clear description, linked issues (`#123`), test results, and docs updates (`docs/`, `README.md`) for user-facing changes. Include screenshots/log snippets when relevant.

## Security & Configuration Tips
- Do not commit secrets. Use `examples/config/.env.example` to document vars; keep `.env` in `.gitignore`.
- Prefer configuration via environment variables; log sensitive values only at safe levels.
- Before release, run `scripts/check_ready_to_publish.sh` and ensure tests pass.

