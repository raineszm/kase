# Repository Guidelines

## Project Structure & Module Organization
- `src/kase/` contains the application code. The CLI entry point is `src/kase/cli.py` and TUI modules live under `src/kase/tui/`.
- `tests/` holds unit, integration, and widget snapshot tests. Snapshot fixtures live in `tests/integration/__snapshots__/` and `tests/integration/widgets/__snapshots__/`.
- `snap/` contains Snap packaging metadata. `CHANGELOG.md` is managed via Changie (`.changes/`).

## Build, Test, and Development Commands
- `uv sync --group dev` installs development dependencies.
- `./hack.sh` sets up pre-commit hooks and runs them once.
- `uv run kase --help` runs the CLI from the local checkout.
- `uv run pytest` runs the full test suite.
- `uv run ruff check .` runs linting; `uv run ruff format .` applies formatting.

## Coding Style & Naming Conventions
- Python target is 3.10+ with 4-space indentation.
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
