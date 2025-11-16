"""Shared fixtures for tests."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_case_dir():
    """Provide a temporary directory for test cases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def create_test_cases():
    """Factory fixture for creating test cases in a directory."""

    def _create_cases(tmpdir, num_cases):
        """Create test cases in the given directory.

        Args:
            tmpdir: Directory to create cases in
            num_cases: Number of test cases to create

        Returns:
            List of created case directories
        """
        case_dirs = []
        for i in range(num_cases):
            case_dir = Path(tmpdir) / str(1000 + i)
            case_dir.mkdir()
            case_meta = case_dir / "case.json"
            case_meta.write_text(
                json.dumps(
                    {
                        "title": f"Test Case {i}",
                        "desc": f"Description {i}",
                        "sf": str(1000 + i),
                        "lp": f"LP#{i}" if i % 2 == 0 else "",
                    }
                )
            )
            case_dirs.append(case_dir)
        return case_dirs

    return _create_cases
