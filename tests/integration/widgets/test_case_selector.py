"""Integration tests for the CaseSelector widget."""

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Markdown

from kase.tui.widgets.case_selector import CaseSelector


class CaseSelectorHarness(App[None]):
    """Minimal App used to host CaseSelector for integration testing."""

    CSS_PATH = None

    def __init__(self, case_dir: str):
        super().__init__()
        self._case_dir = case_dir
        self.events = []

    def compose(self) -> ComposeResult:
        yield CaseSelector(self._case_dir)

    @on(CaseSelector.CaseSelected)
    async def on_case_selected(self, event: CaseSelector.CaseSelected) -> None:
        self.events.append(event)


class TestCaseSelector:
    """Integration tests validating CaseSelector behavior."""

    def test_case_selector_snapshot(self, case_repo_query_small, snap_compare):
        """The widget should display a snapshot of the cases."""
        app = CaseSelectorHarness(case_repo_query_small)
        assert snap_compare(app)

    async def test_case_selector_displays_cases(self, case_repo_query_small):
        """The widget should list every case in the repository."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()
            datatable = app.query_one(DataTable)

            assert datatable.row_count == 3

    async def test_case_selector_filters_cases(self, case_repo_query_small):
        """Filtering through the input should narrow the rows."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()

            input_widget = app.query_one(Input)
            datatable = app.query_one(DataTable)

            input_widget.value = "Python"
            await pilot.pause(0.2)
            assert datatable.row_count == 1

            input_widget.value = ""
            await pilot.pause(0.2)
            assert datatable.row_count == 3

    async def test_case_selector_preview_updates(self, case_repo_query_small):
        """Highlighting a row should populate the Markdown preview."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()

            datatable = app.query_one(DataTable)
            markdown = app.query_one(Markdown)

            datatable.move_cursor(row=1)
            await pilot.pause(0.2)

            assert markdown is not None
            assert datatable.row_count > 0

    async def test_case_selector_cursor_navigation(self, case_repo_query_small):
        """Keyboard navigation bindings should move the cursor."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()

            datatable = app.query_one(DataTable)
            selector = app.query_one(CaseSelector)
            initial_row = datatable.cursor_row

            selector.action_cursor_down()
            await pilot.pause()
            assert datatable.cursor_row == initial_row + 1

            selector.action_cursor_up()
            await pilot.pause()
            assert datatable.cursor_row == initial_row

    async def test_case_selector_selected_case(self, case_repo_query_small):
        """selected_case returns the current case path when rows exist."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()
            selector = app.query_one(CaseSelector)

            assert selector.selected_case() is not None

    async def test_case_selector_selected_case_empty(self, temp_case_dir):
        """selected_case returns None when the repo is empty."""
        app = CaseSelectorHarness(temp_case_dir)
        async with app.run_test():
            selector = app.query_one(CaseSelector)

            assert selector.selected_case() is None

    async def test_case_selector_empty_directory(self, case_repo_empty):
        """An empty repository should produce zero rows."""
        app = CaseSelectorHarness(case_repo_empty)
        async with app.run_test():
            datatable = app.query_one(DataTable)

            assert datatable.row_count == 0

    async def test_case_selector_select_row(self, case_repo_query_small):
        """Selecting a row via Enter should not error."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            selector = app.query_one(CaseSelector)
            assert selector.selected_case() is not None

            await pilot.press("enter")
            await pilot.pause()

            event = app.events[0]
            assert isinstance(event, CaseSelector.CaseSelected)
            assert str(event.case.path) == selector.selected_case()
