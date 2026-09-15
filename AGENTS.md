# Repository Guidelines

## Project Structure & Module Organization
- `src/kase/` contains the application code. The CLI entry point is `src/kase/cli.py` and TUI modules live under `src/kase/tui/`.
- `tests/` holds unit, integration, and widget snapshot tests. Snapshot fixtures live in `tests/integration/__snapshots__/` and `tests/integration/widgets/__snapshots__/`.
- `snap/` contains Snap packaging metadata. `CHANGELOG.md` is managed via Changie (`.changes/`).

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

## Build, Test, and Development Commands
- `uv sync --group dev` installs development dependencies.
- `./hack.sh` sets up pre-commit hooks and runs them once.
- `uv run kase --help` runs the CLI from the local checkout.
- `uv run pytest` runs the full test suite.
- `uv run pytest --cov` runs tests with coverage.

## Coding Style & Naming Conventions
- Python target is 3.14+ with 4-space indentation.
- Formatting and linting are enforced by Ruff (line length 88, double quotes, sorted imports).
- Use `snake_case` for functions/variables and `PascalCase` for classes; test files follow `test_*.py`.

## Testing Guidelines
- Tests use `pytest` with `pytest-asyncio` and `pytest-textual-snapshot` for TUI snapshots.
- Prefer adding coverage for new logic in `tests/unit/` and update snapshot tests when UI changes.
- Run a focused file with `uv run pytest tests/unit/test_cli.py`.

## Commit & Pull Request Guidelines
- Commit messages in history use short, imperative phrases (e.g., "add import command", "refactor CaseSelector").
- For user-facing changes, add a Changie entry in `.changes/` and update docs if behavior changes.
- PRs should include a clear description, testing notes, and screenshots for TUI changes.

## Configuration Notes
- The app reads `CASE_DIR` to locate case directories (defaults to `~/cases`). Mention new config knobs in `README.md`.
