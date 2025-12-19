import asyncio
from pathlib import Path
from typing import override

from rapidfuzz import utils
from rapidfuzz.fuzz import partial_ratio
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Input, Markdown

from ...cases import Case, CaseRepo


class CaseSelector(Widget):
    class CaseSelected(Message):
        def __init__(self, case: Case):
            super().__init__()
            self.case = case

    BINDINGS = [
        Binding("ctrl+n", "cursor_down", "Move cursor down", priority=True),
        Binding("ctrl+p", "cursor_up", "Move cursor up", priority=True),
        Binding("enter", "select_row", "Select row", priority=True),
    ]

    DEFAULT_CSS = """
    .caselist {
        width: 1fr;
        height: 100%;
    }

    .preview {
        width: 1fr;
        height: 100%;
    }
    """

    def __init__(self, case_dir: str, initial_prompt: str = ""):
        super().__init__()

        self.repo = CaseRepo(case_dir)
        self.filter_text = initial_prompt
        self.update_task = None

    @override
    def compose(self):
        with Horizontal():
            yield DataTable[str](
                cursor_type="row", zebra_stripes=True, classes="caselist"
            )
            yield Markdown(classes="preview")
        yield Input(
            self.filter_text, placeholder="Filter", compact=True, select_on_focus=False
        )

    def on_mount(self):
        _ = self.query_one(DataTable).add_columns("SF ID", "Title")
        self._reset_table()
        _ = self.query_one(Input).focus()

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        case_folder = event.row_key.value
        preview = self.query_one(Markdown)
        if case_folder is None:
            await preview.update("No case selected")
        else:
            await preview.update(self.repo.case_preview(case_folder))

    async def on_input_changed(self, event: Input.Changed):
        self.filter_text = event.value
        if self.update_task is None or self.update_task.done():
            self.update_task = asyncio.create_task(self._update_case_list())

    async def _update_case_list(self):
        await asyncio.sleep(0.1)
        selected = self.selected_case()
        _ = self.query_one(DataTable).clear()

        if self.filter_text is None or self.filter_text == "":
            return self._reset_table()

        return self._apply_filter(self.filter_text, selected)

    def _reset_table(self):
        for case in self.repo.cases:
            _add_row(self.query_one(DataTable), case)

    def _apply_filter(self, filter_text: str, selected: str | None):
        caselist = self.query_one(DataTable)
        for case in self.repo.cases:
            score = (
                partial_ratio(
                    " ".join([case.sf, case.lp, case.title, case.desc]),
                    filter_text,
                    processor=utils.default_process,
                )
                / 100.0
            )
            if score > 0.8:
                _add_row(caselist, case)
                if selected is not None and str(case.path) == selected:
                    caselist.move_cursor(row=caselist.get_row_index(selected))
        if selected is None:
            caselist.move_cursor(row=0)

    def selected_case(self) -> str | None:
        caselist = self.query_one(DataTable)
        if caselist.row_count == 0:
            return None
        # Typechecker doesn't know that Reactive[T] casts to T
        # noinspection PyTypeChecker
        return caselist.coordinate_to_cell_key(caselist.cursor_coordinate).row_key.value

    def action_cursor_up(self):
        self.query_one(DataTable).action_cursor_up()

    def action_cursor_down(self):
        self.query_one(DataTable).action_cursor_down()

    def action_select_row(self):
        if case_folder := self.selected_case():
            self.post_message(self.CaseSelected(Case.from_folder(Path(case_folder))))


def _add_row(table: DataTable, case: Case):
    _ = table.add_row(
        case.sf,
        case.title,
        key=str(case.path),
    )
