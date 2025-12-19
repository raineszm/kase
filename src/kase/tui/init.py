from typing import Unpack, override

from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Button, Input, Label, TextArea

from ..cases import CaseRepo
from ..types import AppOptions


class InitApp(App[str]):
    def __init__(self, case_dir: str, **kwargs: Unpack[AppOptions]):
        super().__init__(**kwargs)

        self.repo = CaseRepo(case_dir)

    @override
    def compose(self):
        with Horizontal():
            yield Label(
                "Case Name:",
            )
            yield Input(id="case_name_input", placeholder="[1234] Example Case Title")
        with Horizontal():
            yield Label("LP Bug (optional):")
            yield Input(id="lp_bug_input")
        yield Label("Description:")
        yield TextArea()
        yield Button("Create", variant="primary", flat=True)

    def on_button_pressed(self, _event: Button.Pressed):
        name = self.query_one("#case_name_input", Input).value
        lp_bug = self.query_one("#lp_bug_input", Input).value
        description = self.query_one(TextArea).text

        if self.repo.create_case(name=name, lp=lp_bug, description=description):
            self.exit("Case created successfully.")
