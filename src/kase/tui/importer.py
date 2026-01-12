import os
from collections import OrderedDict
from pathlib import Path
from typing import Unpack, cast, final, override

from textual import on
from textual.app import App
from textual.widgets import Footer, Header

from kase.cases import Case, CaseRepo
from kase.importer import SalesforceCSV
from kase.tui.widgets.case_selector import CaseSelector
from kase.types import AppOptions


@final
class ImporterApp(App[list[Case]]):
    TITLE = "Select cases to import"
    COMMAND_PALETTE_BINDING = "ctrl+shift+p"

    def __init__(
        self,
        case_dir: str,
        csv_file: Path,
        initial_prompt: str = "",
        **kwargs: Unpack[AppOptions],
    ):
        super().__init__(**kwargs)

        self._case_dir = case_dir
        self.salesforce_csv = SalesforceCSV(
            csv_file, Path(os.path.expanduser(case_dir))
        )
        self._initial_prompt = initial_prompt

    @override
    def compose(self):
        repo = CaseRepo(self._case_dir)
        existing_case_ids = {case.sf for case in repo.cases}
        yield Header()
        yield CaseSelector(
            initial_prompt=self._initial_prompt,
            cases=OrderedDict({case.sf: case for case in self.salesforce_csv.cases()}),
            enable_multiselect=True,
            exclude_ids=existing_case_ids,
        )
        yield Footer()

    @on(CaseSelector.CasesSubmitted)
    def action_select_rows(self, event: CaseSelector.CasesSubmitted):
        cast(ImporterApp, self.app).exit(event.cases, return_code=0)
