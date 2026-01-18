"""Shared fixtures for tests."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def temp_case_dir(fs):
    """Provide a temporary directory for test cases using pyfakefs."""
    case_dir = "/cases"
    fs.create_dir(case_dir)
    return case_dir


@pytest.fixture
def temp_case_dir_real(tmp_path):
    """Provide a real temporary directory for tests that need real filesystem access.

    Use this for snapshot tests or tests that interact with external tools.
    """
    case_dir = tmp_path / "cases"
    case_dir.mkdir()
    return str(case_dir)


@pytest.fixture
def create_test_cases():
    """Factory fixture for creating test cases in a directory.

    Works with both pyfakefs and real filesystem.
    """

    def _create_cases(tmpdir, num_cases, fs=None):
        """Create test cases in the given directory.

        Args:
            tmpdir: Directory to create cases in
            num_cases: Number of test cases to create
            fs: Optional pyfakefs instance (if None, uses real filesystem)

        Returns:
            List of created case directories
        """
        case_dirs = []
        for i in range(num_cases):
            case_dir = Path(tmpdir) / str(1000 + i)
            if fs:
                fs.create_dir(case_dir)
                fs.create_file(
                    case_dir / "case.json",
                    contents=json.dumps(
                        {
                            "title": f"Test Case {i}",
                            "desc": f"Description {i}",
                            "sf": str(1000 + i),
                            "lp": f"LP#{i}" if i % 2 == 0 else "",
                        }
                    ),
                )
            else:
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


@pytest.fixture(scope="session")
def case_repo_50_cases(tmp_path_factory):
    """Create a reusable case repo with 50 pre-created cases.

    This fixture is session-scoped and creates a temporary directory with 50 cases
    that can be reused across all tests that don't require mutation.
    """
    tmpdir = tmp_path_factory.mktemp("case_repo_50")

    # Create 50 test cases
    for i in range(50):
        case_dir = tmpdir / str(1000 + i)
        case_dir.mkdir()
        case_meta = case_dir / "case.json"
        case_meta.write_text(
            json.dumps(
                {
                    "title": f"Test Case {i}",
                    "desc": f"Description for test case {i}",
                    "sf": str(1000 + i),
                    "lp": f"LP#{1000 + i}" if i % 3 == 0 else "",
                }
            )
        )

    return str(tmpdir)


@pytest.fixture(scope="session")
def case_repo_query_small(tmp_path_factory):
    """Create a small reusable case repo used by QueryApp tests.

    Contains three specific cases used by assertions in tests:
    - SF 1234: First Test Case
    - SF 5678: Second Test Case
    - SF 9999: Python Related Case (used for filtering assertions)
    """
    tmpdir = tmp_path_factory.mktemp("case_repo_query_small")

    cases = [
        ("1234", "First Test Case", "First description", "LP#1111"),
        ("5678", "Second Test Case", "Second description", "LP#2222"),
        ("9999", "Python Related Case", "Testing Python functionality", ""),
    ]

    for sf, title, desc, lp in cases:
        case_dir = tmpdir / sf
        case_dir.mkdir()
        case_meta = case_dir / "case.json"
        case_meta.write_text(
            json.dumps({"title": title, "desc": desc, "sf": sf, "lp": lp})
        )

    return str(tmpdir)


@pytest.fixture(scope="session")
def case_repo_empty(tmp_path_factory):
    """Create an empty reusable case repo directory for tests that need no cases."""
    tmpdir = tmp_path_factory.mktemp("case_repo_empty")
    return str(tmpdir)
