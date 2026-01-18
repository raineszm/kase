"""Property-based tests for TUI using Hypothesis."""

import json
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from kase.tui.init import InitApp
from kase.tui.query import QueryApp


class TestInitAppProperties:
    """Property-based tests for InitApp."""

    @given(
        sf_number=st.integers(min_value=1, max_value=9999),
        title=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0", "[", "]"],
                blacklist_categories=["Cs", "Cc"],
            ),
        ),
    )
    @settings(
        max_examples=10,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_init_app_handles_various_inputs(self, fs, sf_number, title):
        """Test that InitApp handles various input combinations without crashing."""
        # Create a unique directory for each example
        tmpdir = f"/cases_{sf_number}_{hash(title) % 10000}"
        fs.create_dir(tmpdir)

        app = InitApp(tmpdir)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Fill in the form with generated values
            case_name_input = app.query_one("#case_name_input")
            case_name = f"[{sf_number}] {title}"
            case_name_input.value = case_name

            # Verify form is still responsive
            assert case_name_input.value == case_name


class TestQueryAppProperties:
    """Property-based tests for QueryApp."""

    @given(
        filter_text=st.text(
            max_size=20,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0"],
                blacklist_categories=["Cs", "Cc"],
            ),
        ),
    )
    @settings(max_examples=5, deadline=10000)
    async def test_query_app_handles_various_filters(
        self, case_repo_50_cases, filter_text
    ):
        """Test that QueryApp handles various filter inputs without crashing."""
        app = QueryApp(case_repo_50_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Apply filter
            input_widget = app.query_one("Input")
            input_widget.value = filter_text
            await pilot.pause(0.1)

            # The app should not crash regardless of filter
            datatable = app.query_one("DataTable")
            # Row count should be between 0 and 50 (the number of cases in the repo)
            assert 0 <= datatable.row_count <= 50

    @given(
        case_count=st.integers(min_value=1, max_value=5),
    )
    @settings(
        max_examples=5,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_query_app_navigation_with_various_counts(self, fs, case_count):
        """Test navigation works with various numbers of cases."""
        # Create a unique directory for each example
        tmpdir = f"/cases_nav_{case_count}"
        fs.create_dir(tmpdir)

        # Create test cases
        for i in range(case_count):
            case_dir = Path(tmpdir) / str(1000 + i)
            fs.create_dir(case_dir)
            fs.create_file(
                case_dir / "case.json",
                contents=json.dumps(
                    {
                        "title": f"Case {i}",
                        "desc": f"Desc {i}",
                        "sf": str(1000 + i),
                        "lp": "",
                    }
                ),
            )

        app = QueryApp(tmpdir)
        async with app.run_test() as pilot:
            await pilot.pause()

            datatable = app.query_one("DataTable")
            initial_row = datatable.cursor_row

            # Try navigating down
            await pilot.press("ctrl+n")
            await pilot.pause()

            # Cursor should move or stay at boundary
            if case_count > 1:
                assert datatable.cursor_row >= initial_row

            # Should be able to navigate back
            assert 0 <= datatable.cursor_row < case_count
