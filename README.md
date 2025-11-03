# Kase

A Python project with automated code quality tools.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [pre-commit](https://pre-commit.com/) for automated code quality checks.

### Quick Setup

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up the project and pre-commit hooks**:

   ```bash
   ./hack.sh
   ```

That's it! The script will:

- Install all development dependencies
- Set up pre-commit hooks
- Run initial code formatting and linting

## Style

- The project uses [ruff](https://astral.sh/ruff) for linting and formatting.

## Usage

```bash
uv run kase --help
```
