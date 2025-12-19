# Kase

A fuzzy finder tool for quickly navigating Salesforce support cases. Kase helps you organize and quickly access case directories with integrated shell navigation.

## Installation

Install using uv:

```bash
uv tool install .
```

Or for development:

```bash
uv sync --group dev
```

## Quick Start

1. **Set up shell integration** (required for cd functionality):

   ```bash
   # Add to your shell config (~/.bashrc, ~/.zshrc, etc.)
   eval "$(kase shell)"

   # Or manually add the function:
   jk() {
       dir=$(kase query) && cd "$dir"
   }
   ```

Currently only bash compatible shells are supported.

The name of the function is configurable with the `--jump-cmd` flag.

2. **Set your cases directory** (optional):

By default, Kase will use `~/cases` as the directory for your cases, but you can override this by setting the `CASE_DIR` environment variable.

```bash
export CASE_DIR="~/my-cases"  # defaults to ~/cases
```

3. **Initialize your first case**:

   ```bash
   kase init
   ```

4. **Navigate to cases**:
   ```bash
   jk  # fuzzy search and cd to selected case
   ```

![Screenshot of Kase fuzzy-finder](tests/integration/__snapshots__/test_query_app/TestQueryApp.test_query_app_compose_snapshot.raw)

## Usage

### Commands

The most important commands are:

- **`kase shell`** - Output shell integration code
- **`kase init`** - Create a new case with interactive prompts
- **`kase` or `kase query`** - Open fuzzy finder to select and navigate to a case

### Case Initialization Data

When you run `kase init`, you'll be prompted for:

1. **Case Name** - Enter in the format `[1234] Example Case Title` (case number in brackets followed by title)

- This is what you get by copying and pasting from the Salesforce case page.

2. **LP Bug** - Optional Launchpad bug number if related
3. **Description** - Multi-line description of the case

Kase will then create a case directory using the case number.

## Case Directory Layout

Kase expects and creates the following structure:

```
~/cases/  (or your $CASE_DIR)
├── 1234/                      # Directory named by case number
│   └── case.json              # Case metadata and details
├── 5678/
│   └── case.json
└── ...
```

Each case directory contains a `case.json` file with structured metadata:

```json
{
  "title": "Example Case Title",
  "desc": "Detailed case description...",
  "sf": "1234",
  "lp": "1234567"
}
```

Where:

- `title` - The case title (extracted from the case name)
- `desc` - The description you provided during initialization
- `sf` - The Salesforce case number (extracted from the case name)
- `lp` - Optional Launchpad bug number

## Development Setup

This project uses

- [uv](https://docs.astral.sh/uv/) for python project management
- [ruff](https://docs.astral.sh/ruff/) for formatting and linting
- [pre-commit](https://pre-commit.com/) for pre-commit hooks
- [changie](https://github.com/itchyny/changie) for changelog management

### Quick Setup

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up the project and pre-commit hooks**:
   ```bash
   ./hack.sh
   ```
