from collections import OrderedDict
from typing import Unpack, cast, final, override

from textual import on
from textual.app import App
from textual.widgets import Footer, Header

from kase.cases import Case, CaseRepo
from kase.tui.widgets.case_selector import CaseSelector

from ..types import AppOptions


@final
class QueryApp(App[Case]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    def __init__(
        self,
        case_dir: str,
        initial_prompt: str = "",
        **kwargs: Unpack[AppOptions],
    ):
        super().__init__(**kwargs)

        self.repo = CaseRepo(case_dir)
        self._initial_prompt = initial_prompt

    @override
    def compose(self):
        yield Header()
        yield CaseSelector(
            initial_prompt=self._initial_prompt,
            cases=OrderedDict({case.sf: case for case in self.repo.cases}),
        )
        yield Footer()

    @on(CaseSelector.CaseSelected)
    def action_select_row(self, event: CaseSelector.CaseSelected):
        cast(QueryApp, self.app).exit(event.case, return_code=0)
