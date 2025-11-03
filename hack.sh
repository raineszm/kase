#!/bin/bash

# Setup script for pre-commit hooks in the kase project

set -e

echo "🔧 Setting up pre-commit hooks for kase project..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &>/dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first."
    echo "   Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Install development dependencies (including pre-commit)
echo "📦 Installing development dependencies..."
uv sync --group dev

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install

# Run pre-commit on all files to ensure everything works
echo "🧹 Running pre-commit on all files..."
uv run pre-commit run --all-files

echo "✅ Pre-commit setup complete!"
echo ""
echo "Now pre-commit will automatically run on every commit."
echo "To run pre-commit manually: uv run pre-commit run --all-files"
echo "To update hooks: uv run pre-commit autoupdate"
