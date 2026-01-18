#!/bin/bash
# Playground script for testing kase with sample data
#
# Creates a temporary copy of the sample case repo and spawns a shell
# with CASE_DIR pointing to it. Changes made in the playground are
# isolated and discarded when the shell exits.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_REPO="$SCRIPT_DIR/case_repo"
SAMPLE_CSV="$SCRIPT_DIR/import.csv"

if [[ ! -d "$SAMPLE_REPO" ]]; then
    echo "Error: Sample case repo not found at $SAMPLE_REPO"
    exit 1
fi

# Create temporary directory
TMPDIR=$(mktemp -d -t kase-playground.XXXXXX)

echo "Setting up playground in $TMPDIR"
echo ""

# Copy sample case repo to temp directory
cp -r "$SAMPLE_REPO" "$TMPDIR/cases"

# Also copy the import.csv for easy access
if [[ -f "$SAMPLE_CSV" ]]; then
    cp "$SAMPLE_CSV" "$TMPDIR/import.csv"
fi

echo "Playground ready!"
echo ""
echo "  CASE_DIR=$TMPDIR/cases"
echo "  Sample import.csv available at: $TMPDIR/import.csv"
echo ""
echo "Sample commands to try:"
echo "  kase query              # Fuzzy search through sample cases"
echo "  kase import import.csv  # Import cases from sample CSV"
echo "  kase init 99999         # Initialize a new case"
echo ""
echo "Changes are isolated to this session and will be discarded on exit."
echo "Type 'exit' to leave the playground."
echo ""

# Spawn a shell with CASE_DIR set
cd "$TMPDIR"
export CASE_DIR="$TMPDIR/cases"
export PS1="(kase-playground) $PS1"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up playground at $TMPDIR"
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

# Spawn the user's preferred shell
exec "${SHELL:-/bin/bash}"
