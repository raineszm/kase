"""Integration tests for the CaseSelector widget."""

import pytest

from kase.tui.case_selector import CaseSelector


@pytest.fixture
def case_selector_test_cases(case_repo_query_small):
    """Provide path to a small, pre-created case repo for CaseSelector tests."""
    return case_repo_query_small


class TestCaseSelector:
    """Integration tests for CaseSelector widget."""

    async def test_case_selector_displays_cases(self, case_selector_test_cases):
        """Test that CaseSelector displays all cases."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(case_selector_test_cases)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Check that datatable has rows
            selector = app.query_one(CaseSelector)
            assert selector.caselist.row_count == 3

    async def test_case_selector_filter_cases(self, case_selector_test_cases):
        """Test filtering cases through the input."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(case_selector_test_cases)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Get the selector and its input widget
            selector = app.query_one(CaseSelector)
            selector.input.value = "Python"

            # Wait for filtering to complete
            await pilot.pause(0.2)

            # Check that only matching cases are shown
            assert selector.caselist.row_count == 1

    async def test_case_selector_cursor_navigation(self, case_selector_test_cases):
        """Test cursor navigation actions work."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(case_selector_test_cases)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            selector = app.query_one(CaseSelector)
            initial_row = selector.caselist.cursor_row

            # Test action_cursor_down directly
            selector.action_cursor_down()
            await pilot.pause()

            assert selector.caselist.cursor_row == initial_row + 1

            # Test action_cursor_up directly
            selector.action_cursor_up()
            await pilot.pause()

            assert selector.caselist.cursor_row == initial_row

    async def test_case_selector_emits_case_selected_event(
        self, case_selector_test_cases
    ):
        """Test that CaseSelector emits CaseSelected event."""
        from textual.app import App

        class TestApp(App):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.case_selected_path = None

            def compose(self):
                yield CaseSelector(case_selector_test_cases)

            def on_case_selector_case_selected(self, event: CaseSelector.CaseSelected):
                self.case_selected_path = event.case_path

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press enter to select the first row
            await pilot.press("enter")
            await pilot.pause()

            # Check that the event was received
            assert app.case_selected_path is not None

    async def test_case_selector_emits_case_highlighted_event(
        self, case_selector_test_cases
    ):
        """Test that CaseSelector emits CaseHighlighted event."""
        from textual.app import App

        class TestApp(App):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.case_highlighted_path = None

            def compose(self):
                yield CaseSelector(case_selector_test_cases)

            def on_case_selector_case_highlighted(
                self, event: CaseSelector.CaseHighlighted
            ):
                self.case_highlighted_path = event.case_path

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.2)

            # Check that an initial highlight event was received
            assert app.case_highlighted_path is not None

    async def test_case_selector_selected_case(self, case_selector_test_cases):
        """Test selected_case method."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(case_selector_test_cases)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            selector = app.query_one(CaseSelector)
            selected = selector.selected_case()
            # With 3 cases, there should be a selection
            assert selected is not None

    async def test_case_selector_selected_case_empty(self, temp_case_dir):
        """Test selected_case with no cases."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(temp_case_dir)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            selector = app.query_one(CaseSelector)
            selected = selector.selected_case()
            assert selected is None

    async def test_case_selector_reset_filter(self, case_selector_test_cases):
        """Test resetting the filter."""
        from textual.app import App

        class TestApp(App):
            def compose(self):
                yield CaseSelector(case_selector_test_cases)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            selector = app.query_one(CaseSelector)

            # Apply a filter
            selector.input.value = "Python"
            await pilot.pause(0.2)
            assert selector.caselist.row_count == 1

            # Clear the filter
            selector.input.value = ""
            await pilot.pause(0.2)
            assert selector.caselist.row_count == 3
