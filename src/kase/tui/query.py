from typing import Unpack, cast, final, override

from textual.app import App
from textual.widgets import Footer, Header

from ..types import AppOptions
from .case_selector import CaseSelector


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

    def on_case_selector_case_selected(self, event: CaseSelector.CaseSelected):
        cast(QueryApp, self.app).exit(str(event.case.path), return_code=0)

    def selected_case(self) -> str | None:
        """Get the currently selected case path from the selector widget."""
        selector = self.query_one(CaseSelector)
        return selector.selected_case()
