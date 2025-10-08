from typing_extensions import override
from textual.app import App
from textual.driver import Driver
from textual.types import CSSPathType
from textual.widgets import Header, Footer, DataTable
from glob import glob
import os.path
import json
from pathlib import Path
from typing import final, cast, Unpack, TypedDict
from collections.abc import Iterable


class CaseRepo:
    def __init__(self, case_dir: str):
        self.case_dir: str = os.path.expanduser(case_dir)

    @property
    def metadata(self) -> list[Path]:
        return [Path(f) for f in glob(f"{self.case_dir}/*/case.json")]

    @property
    def rows(self) -> Iterable[dict[str, str]]:
        for meta in self.metadata:
            with meta.open("r") as f:
                data = json.load(f)
                data["path"] = str(meta.parent)
                yield data


@final
class VimTable(DataTable[str]):
    BINDINGS = [
        ("j", "cursor_down", "Move cursor down"),
        ("k", "cursor_up", "Move cursor up"),
        ("enter", "select_row", "Select row"),
    ]

    def action_select_row(self):
        case_folder = self.coordinate_to_cell_key(self.cursor_coordinate).row_key.value
        cast(KaseApp, self.app).exit(case_folder, return_code=0)


class AppOptions(TypedDict, total=False):
    driver_class: type[Driver] | None
    css_path: CSSPathType | None
    watch_css: bool
    ansi_color: bool


@final
class KaseApp(App[str]):
    TITLE = "Your cases!"

    def __init__(self, case_dir: str = "~/cases", **kwargs: Unpack[AppOptions]):
        self.repo = CaseRepo(case_dir)
        super().__init__(**kwargs)

    @override
    def compose(self):
        yield Header()
        yield VimTable(cursor_type="row", zebra_stripes=True)
        yield Footer()

    def on_mount(self):
        table = self.query_one(VimTable)
        _ = table.add_columns("SF", "LP", "Title")
        for case in self.repo.rows:
            _ = table.add_row(
                case.get("sf", ""),
                case.get("lp", ""),
                case.get("title", ""),
                key=case["path"],
            )


def main():
    app = KaseApp("~/Programming/Sandbox/casetest/cases")
    result = app.run()
    if result is not None:
        print(result)
