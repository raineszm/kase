import asyncio

from rapidfuzz import utils
from rapidfuzz.fuzz import partial_ratio
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import DataTable, Input, Markdown, Static

from ..cases import Case, CaseRepo


class CaseSelector(Static):
    """A widget that displays cases with fuzzy filtering.

    Raises events when a case is selected.
    """

    BINDINGS = [
        Binding("ctrl+n", "cursor_down", "Move cursor down", priority=True),
        Binding("ctrl+p", "cursor_up", "Move cursor up", priority=True),
        Binding("enter", "select_row", "Select row", priority=True),
    ]

    CSS = """
    CaseSelector {
        width: 1fr;
        height: 100%;
    }

    CaseSelector .caselist {
        width: 1fr;
        height: 100%;
    }

    CaseSelector .preview {
        width: 1fr;
        height: 100%;
    }

    CaseSelector Input {
        width: 1fr;
        dock: bottom;
    }
    """

    class CaseSelected(Message):
        """Event raised when a case is selected."""

        def __init__(self, case: Case) -> None:
            super().__init__()
            self.case = case

    class CaseHighlighted(Message):
        """Event raised when a case is highlighted."""

        def __init__(self, case: Case | None) -> None:
            super().__init__()
            self.case = case

    def __init__(self, case_dir: str = "~/cases", **kwargs):
        super().__init__(**kwargs)
        self.repo = CaseRepo(case_dir)
        self.filter_text = None
        self.update_task = None
        # Cache cases to avoid re-reading from disk on each lookup
        self._cases_cache = list(self.repo.cases)

    def compose(self):
        with Horizontal():
            self.caselist = DataTable[str](
                cursor_type="row", zebra_stripes=True, classes="caselist"
            )
            yield self.caselist
            yield Markdown(classes="preview")
        self.input = Input(placeholder="Filter", compact=True)
        yield self.input

    def on_mount(self):
        _ = self.caselist.add_columns("SF ID", "LP Bug", "Title", "Description")
        self._reset_table()
        _ = self.input.focus()

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        case_path = event.row_key.value if event.row_key else None
        preview = self.query_one(Markdown)
        if case_path is None:
            await preview.update("No case selected")
            self.post_message(self.CaseHighlighted(None))
        else:
            case = self._get_case_by_path(case_path)
            if case:
                await preview.update(self._case_preview(case))
                self.post_message(self.CaseHighlighted(case))
            else:
                await preview.update("No case selected")
                self.post_message(self.CaseHighlighted(None))

    async def on_input_changed(self, event: Input.Changed):
        self.filter_text = event.value
        if self.update_task is None or self.update_task.done():
            self.update_task = asyncio.create_task(self._update_case_list())

    async def _update_case_list(self):
        await asyncio.sleep(0.1)
        selected = self.selected_case()
        _ = self.caselist.clear()

        if self.filter_text is None or self.filter_text == "":
            return self._reset_table()

        return self._apply_filter(self.filter_text, selected)

    def _reset_table(self):
        for case in self._cases_cache:
            self._add_row(case)

    def _apply_filter(self, filter_text: str, selected: str | None):
        for case in self._cases_cache:
            score = (
                partial_ratio(
                    " ".join([case.sf, case.lp, case.title, case.desc]),
                    filter_text,
                    processor=utils.default_process,
                )
                / 100.0
            )
            if score > 0.8:
                self._add_row(case)
                if selected is not None and str(case.path) == selected:
                    try:
                        self.caselist.move_cursor(
                            row=self.caselist.get_row_index(selected)
                        )
                    except KeyError:
                        # Selected case is no longer in the filtered list
                        pass
        if selected is None and self.caselist.row_count > 0:
            self.caselist.move_cursor(row=0)

    def selected_case(self) -> str | None:
        if self.caselist.row_count == 0:
            return None
        # Typechecker doesn't know that Reactive[T] casts to T
        # noinspection PyTypeChecker
        return self.caselist.coordinate_to_cell_key(
            self.caselist.cursor_coordinate
        ).row_key.value

    def action_cursor_up(self):
        self.caselist.action_cursor_up()

    def action_cursor_down(self):
        self.caselist.action_cursor_down()

    def action_select_row(self):
        if case_path := self.selected_case():
            case = self._get_case_by_path(case_path)
            if case:
                self.post_message(self.CaseSelected(case))

    def _add_row(self, case: Case):
        _ = self.caselist.add_row(
            case.sf,
            case.lp,
            case.title,
            case.desc,
            key=str(case.path),
        )

    def _get_case_by_path(self, path: str) -> Case | None:
        """Get a Case object by its path string."""
        for case in self._cases_cache:
            if str(case.path) == path:
                return case
        return None

    def _case_preview(self, case: Case) -> str:
        """Generate preview markdown for a case."""
        return self.repo.case_preview(str(case.path))
