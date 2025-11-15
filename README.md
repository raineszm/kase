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

### Commands

#### Query Cases

Open a fuzzy finder to select and navigate to a case:

```bash
kase query [CASE_DIR]
```

#### Initialize a New Case

Create a new case interactively:

```bash
kase init
```

#### Import from Salesforce

Import a case directly from a Salesforce URL:

```bash
kase import-case <SALESFORCE_URL>
```

Options:
- `--case-dir`: Specify the directory to store cases (default: `$CASE_DIR` or `~/cases`)
- `--show-browser`: Show the browser window during import (useful for debugging or manual login)

The command will:
1. Open a headless browser (or visible if `--show-browser` is used)
2. Navigate to the Salesforce case URL
3. Prompt for login if not authenticated
4. Extract case information (ID, title, description)
5. Create a new case directory with metadata

Example:

```bash
kase import-case https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view
```

#### Shell Integration

Generate shell integration code:

```bash
kase shell
```

This provides a `jk` function that can be used to quickly navigate to cases.
