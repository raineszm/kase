from typing import Unpack, cast, final, override

from textual import on
from textual.app import App
from textual.widgets import Footer, Header

from kase.tui.widgets.case_selector import CaseSelector

from ..types import AppOptions


@final
class QueryApp(App[str]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    def __init__(
        self,
        initial_prompt: str = "",
        case_dir: str = "~/cases",
        **kwargs: Unpack[AppOptions],
    ):
        super().__init__(**kwargs)

        self.case_dir = case_dir
        self._initial_prompt = initial_prompt

    @override
    def compose(self):
        yield Header()
        yield CaseSelector(
            initial_prompt=self._initial_prompt,
            case_dir=self.case_dir,
        )
        yield Footer()

    @on(CaseSelector.CaseSelected)
    def action_select_row(self, event: CaseSelector.CaseSelected):
        cast(QueryApp, self.app).exit(str(event.case.path), return_code=0)
