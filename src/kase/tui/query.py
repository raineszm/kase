import asyncio
from typing import Unpack, cast, final, override

from rapidfuzz import utils
from rapidfuzz.fuzz import partial_ratio
from textual import on
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Input, Markdown

from kase.tui.widgets.case_selector import CaseSelector

from ..cases import Case, CaseRepo
from ..types import AppOptions


@final
class QueryApp(App[str]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    def __init__(self, case_dir: str = "~/cases", **kwargs: Unpack[AppOptions]):
        super().__init__(**kwargs)

        self.case_dir = case_dir

    @override
    def compose(self):
        yield Header()
        yield CaseSelector(self.case_dir)
        yield Footer()

    @on(CaseSelector.CaseSelected)
    def action_select_row(self, event: CaseSelector.CaseSelected):
        cast(QueryApp, self.app).exit(str(event.case.path), return_code=0)
