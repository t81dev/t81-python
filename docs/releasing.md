# Releasing

## Prerequisites

- PyPI trusted publisher configured for this repository.
- Workflow file present: `.github/workflows/publish.yml`.

## Pre-release Checklist

1. Run local checks:
   - `ruff check .`
   - `mypy src tests`
   - `pytest`
   - `python -m build`
2. Update `CHANGELOG.md` with release notes.
3. Ensure `pyproject.toml` version is correct.

## Tag and Publish

1. Create and push a version tag:
   - `git tag v0.1.0`
   - `git push origin v0.1.0`
2. GitHub Actions `Publish` workflow builds and uploads artifacts to PyPI.

## Post-release

1. Verify package/version on PyPI.
2. Verify install path in a clean virtualenv:
   - `pip install t81-python==0.1.0`
3. Start next iteration in `CHANGELOG.md`.
