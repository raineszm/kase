from typing import final, cast, Unpack, override

from textual.app import App
from textual.widgets import DataTable, Header, Footer

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

    def __init__(self, case_dir: str = "~/cases", **kwargs: Unpack[AppOptions]):
        self.repo = CaseRepo(case_dir)
        super().__init__(**kwargs)

    @override
    def compose(self):
        yield Header()
        yield CaseTable(cursor_type="row", zebra_stripes=True)
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
