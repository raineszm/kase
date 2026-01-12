"""Integration tests for the CaseSelector widget."""

from collections import OrderedDict

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Markdown

from kase.cases import CaseRepo
from kase.tui.widgets.case_selector import CaseSelector


class CaseSelectorHarness(App[None]):
    """Minimal App used to host CaseSelector for integration testing."""

    CSS_PATH = None

    def __init__(
        self,
        case_dir: str,
        enable_multiselect: bool = False,
        exclude_ids: set[str] | None = None,
    ):
        super().__init__()
        self._repo = CaseRepo(case_dir)
        self.events = []
        self.enable_multiselect = enable_multiselect
        self.exclude_ids = exclude_ids

    def compose(self) -> ComposeResult:
        cases = OrderedDict({case.sf: case for case in self._repo.cases})
        yield CaseSelector(
            cases=cases,
            enable_multiselect=self.enable_multiselect,
            exclude_ids=self.exclude_ids,
        )

    @on(CaseSelector.CaseSelected)
    async def on_case_selected(self, event: CaseSelector.CaseSelected) -> None:
        self.events.append(event)

    @on(CaseSelector.CasesSubmitted)
    async def on_cases_submitted(self, event: CaseSelector.CasesSubmitted) -> None:
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
            selected = selector.selected_case()
            assert selected is not None

            await pilot.press("enter")
            await pilot.pause()

            event = app.events[0]
            assert isinstance(event, CaseSelector.CaseSelected)
            assert event.case.sf == selected.sf

    async def test_case_selector_mark_case(self, case_repo_query_small):
        """Marking a case should not error."""
        app = CaseSelectorHarness(case_repo_query_small, enable_multiselect=True)
        async with app.run_test() as pilot:
            await pilot.pause()
            selector = app.query_one(CaseSelector)

            selector.action_toggle_mark()
            await pilot.pause()

            # No exception should be raised.
            # Check if the case is marked
            selected_case = selector.selected_case()
            assert selected_case is not None
            assert str(selected_case.sf) in selector.marked_case_ids

    async def test_case_selector_excludes_cases_by_default(self, case_repo_query_small):
        """Excluded cases should be hidden by default."""
        app = CaseSelectorHarness(case_repo_query_small, exclude_ids={"1234"})
        async with app.run_test() as pilot:
            await pilot.pause()
            datatable = app.query_one(DataTable)

            # Should only show 2 cases (3 total - 1 excluded)
            assert datatable.row_count == 2

    async def test_case_selector_toggle_exclude_shows_excluded(
        self, case_repo_query_small
    ):
        """Toggling exclude should show excluded cases."""
        app = CaseSelectorHarness(case_repo_query_small, exclude_ids={"1234"})
        async with app.run_test() as pilot:
            await pilot.pause()
            datatable = app.query_one(DataTable)
            selector = app.query_one(CaseSelector)

            # Initially 2 cases visible
            assert datatable.row_count == 2

            # Toggle exclude visibility
            selector.action_toggle_exclude()
            await pilot.pause()

            # All 3 cases should be visible now
            assert datatable.row_count == 3

            # Toggle again to hide excluded
            selector.action_toggle_exclude()
            await pilot.pause()

            # Back to 2 cases
            assert datatable.row_count == 2

    async def test_case_selector_exclude_respects_filter(self, case_repo_query_small):
        """Filtering should respect the exclude visibility setting."""
        app = CaseSelectorHarness(case_repo_query_small, exclude_ids={"1234"})
        async with app.run_test() as pilot:
            await pilot.pause()

            input_widget = app.query_one(Input)
            datatable = app.query_one(DataTable)
            selector = app.query_one(CaseSelector)

            # Filter for "Test Case" should match 2 cases but exclude 1
            input_widget.value = "Test Case"
            await pilot.pause(0.2)
            assert datatable.row_count == 1  # Only "5678" matches (1234 excluded)

            # Show excluded cases
            selector.action_toggle_exclude()
            await pilot.pause()

            # Clear and re-apply filter
            input_widget.value = ""
            await pilot.pause(0.2)
            input_widget.value = "Test Case"
            await pilot.pause(0.2)

            # Now both matching cases should be visible
            assert datatable.row_count == 2

    async def test_case_selector_toggle_exclude_disabled_when_empty(
        self, case_repo_query_small
    ):
        """toggle_exclude action should be disabled when exclude_ids is empty."""
        app = CaseSelectorHarness(case_repo_query_small)
        async with app.run_test() as pilot:
            await pilot.pause()
            selector = app.query_one(CaseSelector)

            # check_action should return False for toggle_exclude when no exclude_ids
            assert selector.check_action("toggle_exclude", None) is False

    async def test_case_selector_toggle_exclude_enabled_with_excludes(
        self, case_repo_query_small
    ):
        """toggle_exclude action should be enabled when exclude_ids has values."""
        app = CaseSelectorHarness(case_repo_query_small, exclude_ids={"1234"})
        async with app.run_test() as pilot:
            await pilot.pause()
            selector = app.query_one(CaseSelector)

            # check_action should return True for toggle_exclude when exclude_ids set
            assert selector.check_action("toggle_exclude", None) is True
