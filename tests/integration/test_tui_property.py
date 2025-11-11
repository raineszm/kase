"""Property-based tests for TUI using Hypothesis."""

import json
import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from kase.tui.init import InitApp
from kase.tui.query import QueryApp


class TestInitAppProperties:
    """Property-based tests for InitApp."""

    @given(
        sf_number=st.integers(min_value=1, max_value=99999),
        title=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0"],
                blacklist_categories=["Cs", "Cc"],
            ),
        ),
        lp_bug=st.one_of(st.none(), st.text(max_size=50)),
        description=st.text(
            max_size=500,
            alphabet=st.characters(
                blacklist_characters=["\0"], blacklist_categories=["Cs"]
            ),
        ),
    )
    async def test_init_app_handles_various_inputs(
        self, sf_number, title, lp_bug, description
    ):
        """Test that InitApp handles various input combinations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = InitApp(tmpdir)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Fill in the form
                case_name_input = app.query_one("#case_name_input")
                lp_bug_input = app.query_one("#lp_bug_input")
                text_area = app.query_one("TextArea")

                # Set values - hypothesis will test various combinations
                case_name = f"[{sf_number}] {title}"
                case_name_input.value = case_name
                lp_bug_input.value = lp_bug or ""
                text_area.text = description

                # The app should not crash regardless of input
                await pilot.pause()

                # Verify form is still responsive
                assert case_name_input.value == case_name
                assert lp_bug_input.value == (lp_bug or "")


class TestQueryAppProperties:
    """Property-based tests for QueryApp."""

    @given(
        num_cases=st.integers(min_value=0, max_value=20),
        filter_text=st.text(
            max_size=50,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0"],
                blacklist_categories=["Cs", "Cc"],
            ),
        ),
    )
    async def test_query_app_handles_various_filters(self, num_cases, filter_text):
        """Test that QueryApp handles various filter inputs and case counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test cases
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

            app = QueryApp(tmpdir)
            async with app.run_test() as pilot:
                await pilot.pause()

                # Apply filter
                input_widget = app.query_one("Input")
                input_widget.value = filter_text
                await pilot.pause(0.2)

                # The app should not crash regardless of filter
                datatable = app.query_one("DataTable")
                # Row count should be between 0 and num_cases
                assert 0 <= datatable.row_count <= num_cases

    @given(
        case_count=st.integers(min_value=1, max_value=10),
    )
    async def test_query_app_navigation_with_various_counts(self, case_count):
        """Test navigation works with various numbers of cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test cases
            for i in range(case_count):
                case_dir = Path(tmpdir) / str(1000 + i)
                case_dir.mkdir()
                case_meta = case_dir / "case.json"
                case_meta.write_text(
                    json.dumps(
                        {
                            "title": f"Case {i}",
                            "desc": f"Desc {i}",
                            "sf": str(1000 + i),
                            "lp": "",
                        }
                    )
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

                # Try navigating up
                await pilot.press("ctrl+p")
                await pilot.pause()

                # Should be able to navigate back
                assert 0 <= datatable.cursor_row < case_count
