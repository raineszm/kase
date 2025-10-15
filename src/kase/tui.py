from typing import final, cast, Unpack, override

from textual.app import App
from textual.widgets import DataTable, Header, Footer, Input, Markdown
from textual.containers import Horizontal
from textual.fuzzy import Matcher
from textual.binding import Binding

from .cases import CaseRepo
from .types import AppOptions


@final
class CaseTable(DataTable[str]):
    @property
    def selected_case(self) -> str | None:
        if self.row_count == 0:
            return
        return self.coordinate_to_cell_key(self.cursor_coordinate).row_key.value

    def action_select_row(self):
        if case_folder := self.selected_case:
            cast(KaseApp, self.app).exit(case_folder, return_code=0)


@final
class KaseApp(App[str]):
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
        self.repo = CaseRepo(case_dir)
        super().__init__(**kwargs)

    @override
    def compose(self):
        yield Header()
        with Horizontal():
            self.caselist = CaseTable(
                cursor_type="row", zebra_stripes=True, classes="caselist"
            )
            yield self.caselist
            yield Markdown(classes="preview")
        self.input = Input(placeholder="Filter", compact=True)
        yield self.input
        yield Footer()

    def on_mount(self):
        _ = self.caselist.add_columns("SF ID", "LP Bug", "Title", "Description")
        for case in self.repo.rows:
            self._add_row(case)
        self.input.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        case_folder = event.row_key.value
        preview = self.query_one(Markdown)
        if case_folder is None:
            preview.update("No case selected")
        else:
            preview.update(self.repo.case_preview(case_folder))

    def on_input_changed(self, event: Input.Changed) -> None:
        selected = self.caselist.selected_case
        self.caselist.clear()

        if event.value == "":
            for case in self.repo.rows:
                self._add_row(case)
            return

        m = Matcher(event.value)
        for case in self.repo.rows:
            score = m.match(
                " ".join(
                    [
                        case.get("sf", ""),
                        case.get("lp", ""),
                        case.get("title", ""),
                        case.get("description", ""),
                    ]
                )
            )
            if score > 0.8:
                self._add_row(case)
                if selected is not None and case["path"] == selected:
                    self.caselist.move_cursor(row=self.caselist.get_row_index(selected))

    def action_cursor_up(self) -> None:
        self.caselist.action_cursor_up()

    def action_cursor_down(self) -> None:
        self.caselist.action_cursor_down()

    def action_select_row(self) -> None:
        self.caselist.action_select_row()

    def _add_row(self, case: dict[str, str]):
        _ = self.caselist.add_row(
            case.get("sf", ""),
            case.get("lp", ""),
            case.get("title", ""),
            case.get("description", ""),
            key=case["path"],
        )
