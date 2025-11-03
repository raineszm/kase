import asyncio
from typing import Unpack, cast, final, override

from rapidfuzz import utils
from rapidfuzz.fuzz import partial_ratio
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import DataTable, Footer, Header, Input, Markdown

from ..cases import Case, CaseRepo
from ..types import AppOptions


@final
class QueryApp(App[str]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    BINDINGS = [
        Binding("ctrl+n", "cursor_down", "Move cursor down", priority=True),
        Binding("ctrl+p", "cursor_up", "Move cursor up", priority=True),
        Binding("enter", "select_row", "Select row", priority=True),
    ]

    CSS = """
    .caselist {
        width: 1fr;
        height: 100%;
    }

    .preview {
        width: 1fr;
        height: 100%;
    }
    """

    def __init__(self, case_dir: str = "~/cases", **kwargs: Unpack[AppOptions]):
        super().__init__(**kwargs)

        self.repo = CaseRepo(case_dir)
        self.caselist = DataTable[str](
            cursor_type="row", zebra_stripes=True, classes="caselist"
        )
        self.input = Input(placeholder="Filter", compact=True)
        self.filter_text = None
        self.update_task = None

    @override
    def compose(self):
        yield Header()
        with Horizontal():
            yield self.caselist
            yield Markdown(classes="preview")
        yield self.input
        yield Footer()

    def on_mount(self):
        _ = self.caselist.add_columns("SF ID", "LP Bug", "Title", "Description")
        self._reset_table()
        _ = self.input.focus()

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
        _ = self.caselist.clear()

        if self.filter_text is None or self.filter_text == "":
            return self._reset_table()

        return self._apply_filter(self.filter_text, selected)

    def _reset_table(self):
        for case in self.repo.cases:
            self._add_row(case)

    def _apply_filter(self, filter_text: str, selected: str | None):
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
                self._add_row(case)
                if selected is not None and str(case.path) == selected:
                    self.caselist.move_cursor(row=self.caselist.get_row_index(selected))
        if selected is None:
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
        if case_folder := self.selected_case():
            cast(QueryApp, self.app).exit(case_folder, return_code=0)

    def _add_row(self, case: Case):
        _ = self.caselist.add_row(
            case.sf,
            case.lp,
            case.title,
            case.desc,
            key=str(case.path),
        )
