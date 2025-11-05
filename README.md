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

2. **Set your cases directory** (optional):
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

## Usage

### Commands

- **`kase` or `kase query`** - Open fuzzy finder to select and navigate to a case
- **`kase init`** - Create a new case with interactive prompts
- **`kase shell`** - Output shell integration code

### Shell Integration

The `jk` function (or whatever you name it) provides the core functionality:
- Opens a fuzzy finder with all your cases
- Allows quick filtering by typing
- Changes directory to the selected case

## Case Initialization

When you run `kase init`, you'll be prompted to:
1. **Case Name** - Enter in format `[1234] Example Case Title` (case number in brackets followed by title)
2. **LP Bug** - Optional Launchpad bug number if related
3. **Description** - Multi-line description of the case

The tool will parse the case name format and create a structured case directory using the case number.

## Directory Structure

Kase expects and creates the following structure:

```
~/cases/  (or your $CASE_DIR)
├── 1234/                      # Directory named by case number
│   └── case.json              # Case metadata and details
├── 5678/
│   └── case.json
└── ...
```

You can add additional files and folders within each case directory as needed:
- `notes.md` - Your investigation notes
- `logs/` - Log files
- `screenshots/` - Screenshots and images
- `attachments/` - Case attachments

### Case Metadata (`case.json`)

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

## Environment Variables

- **`CASE_DIR`** - Directory where cases are stored (default: `~/cases`)

## Shell Integration Setup

### Bash/Zsh
Add to `~/.bashrc` or `~/.zshrc`:
```bash
eval "$(kase shell)"
```

### Fish
Add to `~/.config/fish/config.fish`:
```fish
kase shell | source
```

### Manual Setup
If you prefer not to use `eval`, add this function manually:
```bash
jk() {
    dir=$(kase query) && cd "$dir"
}
```

## Workflow Example

1. **New case comes in via Salesforce**
2. **Run `kase init`** - Enter case name as `[1234] Customer Login Issue`
3. **Add optional LP bug** - If there's a related Launchpad bug
4. **Add description** - Brief description of the issue
5. **Case directory `1234/` is created** with structured metadata in `case.json`
6. **Use `jk`** to quickly navigate to the case
7. **Work in the case directory** - add notes, logs, screenshots
8. **Use `jk`** to switch between cases as needed

## Tips

- **Fuzzy matching**: Type parts of case numbers, customer names, or subjects to filter
- **Recent cases**: Cases are typically sorted by modification time
- **Consistent naming**: The tool helps maintain consistent directory naming
- **Rich metadata**: Case details are preserved in structured JSON format

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

The project uses [ruff](https://astral.sh/ruff) for linting and formatting.
