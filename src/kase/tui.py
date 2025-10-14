from typing import final, cast, Unpack, override

from textual.app import App
from textual.widgets import DataTable, Header, Footer, Input, Markdown
from textual.containers import Horizontal

from .cases import CaseRepo
from .types import AppOptions


@final
class CaseTable(DataTable[str]):
    BINDINGS = [
        ("ctrl+n", "cursor_down", "Move cursor down"),
        ("ctrl+p", "cursor_up", "Move cursor up"),
        ("enter", "select_row", "Select row"),
    ]

    def action_select_row(self):
        case_folder = self.coordinate_to_cell_key(self.cursor_coordinate).row_key.value
        cast(KaseApp, self.app).exit(case_folder, return_code=0)


@final
class KaseApp(App[str]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"
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
        table = self.query_one(CaseTable)
        _ = table.add_columns("SF ID", "LP Bug", "Title", "Description")
        for case in self.repo.rows:
            _ = table.add_row(
                case.get("sf", ""),
                case.get("lp", ""),
                case.get("title", ""),
                case.get("description", ""),
                key=case["path"],
            )
        self.input.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        case_folder = event.row_key.value
        preview = self.query_one(Markdown)
        if case_folder is None:
            preview.update("No case selected")
        else:
            preview.update(self.repo.case_preview(case_folder))
