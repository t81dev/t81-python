# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Required Checks

Run before opening a pull request:

```bash
ruff check .
mypy src tests
pytest
python -m build
```

## Commit Scope

- Keep commits focused and small.
- Include tests for behavior changes.
- Update docs for new CLI/API features.

## Pull Requests

- Explain what changed and why.
- Include validation output summary.
- Reference related issues or roadmap items when applicable.
