from typing import Unpack, cast, final, override

from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Markdown

from ..cases import CaseRepo
from ..types import AppOptions
from .case_selector import CaseSelector


@final
class QueryApp(App[str]):
    TITLE = "Your cases!"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    CSS = """
    .preview {
        width: 1fr;
        height: 100%;
    }
    """

    def __init__(self, case_dir: str = "~/cases", **kwargs: Unpack[AppOptions]):
        super().__init__(**kwargs)
        self.case_dir = case_dir
        self.repo = CaseRepo(case_dir)

    @override
    def compose(self):
        yield Header()
        with Horizontal():
            yield CaseSelector(self.case_dir)
            yield Markdown(classes="preview")
        yield Footer()

    async def on_case_selector_case_highlighted(
        self, event: CaseSelector.CaseHighlighted
    ):
        preview = self.query_one(Markdown)
        if event.case_path is None:
            await preview.update("No case selected")
        else:
            await preview.update(self.repo.case_preview(event.case_path))

    def on_case_selector_case_selected(self, event: CaseSelector.CaseSelected):
        cast(QueryApp, self.app).exit(event.case_path, return_code=0)

    def selected_case(self) -> str | None:
        """Get the currently selected case path from the selector widget."""
        selector = self.query_one(CaseSelector)
        return selector.selected_case()
