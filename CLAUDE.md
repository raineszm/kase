# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
# Install development dependencies
uv sync --group dev

# Set up pre-commit hooks
./hack.sh

# Run the CLI from local checkout
uv run kase --help

# Run full test suite
uv run pytest

# Run a specific test file
uv run pytest tests/unit/test_cli.py

# Run tests with coverage
uv run pytest --cov

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Architecture Overview

Kase is a Textual-based TUI application for navigating Salesforce support case directories with fuzzy search.

**Core Components:**

- `src/kase/cli.py` - Typer CLI entry point. Defines commands: `query` (default), `init`, `import`, `punch`, `shell`
- `src/kase/cases.py` - Data models. `Case` (Pydantic model) represents a case with metadata. `CaseRepo` manages case discovery from `$CASE_DIR` (defaults to `~/cases`)
- `src/kase/tui/` - Textual TUI applications:
  - `query.py` - `QueryApp` for fuzzy-finding and selecting cases
  - `init.py` - `InitApp` for creating new cases interactively
  - `importer.py` - `ImporterApp` for importing cases from Salesforce CSV exports
- `src/kase/tui/widgets/case_selector.py` - Reusable `CaseSelector` widget with fuzzy matching (rapidfuzz), multi-select support, and markdown preview

**Data Flow:**
1. CLI commands instantiate TUI apps with a `CaseRepo`
2. `CaseRepo` scans for `*/case.json` files in the case directory
3. `CaseSelector` displays cases with real-time fuzzy filtering
4. Selected case path is printed to stdout for shell integration (`jk` function)

**Testing:**
- Unit tests in `tests/unit/` for CLI and case logic
- Integration tests in `tests/integration/` including TUI snapshot tests using `pytest-textual-snapshot`
- Snapshots stored in `tests/integration/__snapshots__/`

## Coding Standards

- Python 3.10+, Ruff for formatting/linting (line length 88, double quotes)
- Commit messages: short imperative phrases (e.g., "add import command", "refactor CaseSelector")
- For user-facing changes, add a Changie entry in `.changes/`
