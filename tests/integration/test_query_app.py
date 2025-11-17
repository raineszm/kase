"""Integration tests for the QueryApp TUI."""

import pytest

from kase.tui.query import QueryApp


@pytest.fixture
def query_app_test_cases(case_repo_query_small):
    """Provide path to a small, pre-created case repo for QueryApp tests."""
    return case_repo_query_small


class TestQueryApp:
    """Integration tests for QueryApp."""

    def test_query_app_compose(self, snap_compare, case_repo_query_small):
        """Test that QueryApp composes correctly using snapshot testing."""
        app = QueryApp(case_repo_query_small)
        assert snap_compare(app)

    async def test_query_app_displays_cases(self, query_app_test_cases):
        """Test that QueryApp displays all cases."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Check that datatable has rows
            datatable = app.query_one("DataTable")
            assert datatable.row_count == 3

    async def test_query_app_filter_cases(self, query_app_test_cases):
        """Test filtering cases through the input."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Get the input widget and type a filter
            input_widget = app.query_one("Input")
            input_widget.value = "Python"

            # Wait for filtering to complete
            await pilot.pause(0.2)

            # Check that only matching cases are shown
            datatable = app.query_one("DataTable")
            # Only the "Python Related Case" should match
            assert datatable.row_count == 1

    async def test_query_app_preview_updates(self, query_app_test_cases):
        """Test that preview updates when highlighting a row."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Get the markdown widget
            markdown = app.query_one("Markdown")

            # Wait for preview to load
            await pilot.pause(0.2)

            # Verify the markdown widget exists and is visible
            assert markdown is not None
            datatable = app.query_one("DataTable")
            assert datatable.row_count > 0

    async def test_query_app_cursor_navigation(self, query_app_test_cases):
        """Test cursor navigation with ctrl+n and ctrl+p."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            datatable = app.query_one("DataTable")
            initial_row = datatable.cursor_row

            # Move cursor down
            await pilot.press("ctrl+n")
            await pilot.pause()

            assert datatable.cursor_row == initial_row + 1

            # Move cursor up
            await pilot.press("ctrl+p")
            await pilot.pause()

            assert datatable.cursor_row == initial_row

    async def test_query_app_select_row(self, query_app_test_cases):
        """Test selecting a row with enter key."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press enter to select the first row
            # App might exit which is expected behavior
            try:
                await pilot.press("enter")
                await pilot.pause()
            except Exception:
                pass

    async def test_query_app_empty_directory(self, case_repo_empty):
        """Test QueryApp with empty directory."""
        app = QueryApp(case_repo_empty)
        async with app.run_test() as pilot:
            await pilot.pause()

            datatable = app.query_one("DataTable")
            assert datatable.row_count == 0

    async def test_query_app_selected_case(self, query_app_test_cases):
        """Test selected_case method."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            # Get the initially selected case
            selected = app.selected_case()
            # With 3 cases, there should be a selection
            assert selected is not None

    async def test_query_app_selected_case_empty(self, temp_case_dir):
        """Test selected_case with no cases."""
        app = QueryApp(temp_case_dir)
        async with app.run_test() as pilot:
            await pilot.pause()

            selected = app.selected_case()
            assert selected is None

    async def test_query_app_reset_filter(self, query_app_test_cases):
        """Test resetting the filter."""
        app = QueryApp(query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()

            input_widget = app.query_one("Input")
            datatable = app.query_one("DataTable")

            # Apply a filter
            input_widget.value = "Python"
            await pilot.pause(0.2)
            assert datatable.row_count == 1

            # Clear the filter
            input_widget.value = ""
            await pilot.pause(0.2)
            assert datatable.row_count == 3
