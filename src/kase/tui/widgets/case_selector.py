import asyncio
from collections import OrderedDict
from typing import override

from rapidfuzz import utils
from rapidfuzz.fuzz import partial_ratio
from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Input, Markdown

from ...cases import Case


class CaseSelector(Widget):
    class CaseSelected(Message):
        def __init__(self, case: Case):
            super().__init__()
            self.case = case

    class CasesSubmitted(Message):
        def __init__(self, cases: list[Case]):
            super().__init__()
            self.cases = cases

    BINDINGS = [
        Binding("ctrl+n", "cursor_down", "Move cursor down", priority=True),
        Binding("ctrl+p", "cursor_up", "Move cursor up", priority=True),
        Binding("enter", "select_row", "Submit", priority=True),
        Binding("ctrl+m", "toggle_mark", "Mark/unmark case", priority=True),
        Binding("ctrl+e", "toggle_exclude", "Toggle excluded cases", priority=True),
    ]

    DEFAULT_CSS = """
    .caselist {
        width: 1fr;
        height: 100%;
    }

    .preview {
        width: 1fr;
        height: 100%;
    }
    """

    def __init__(
        self,
        cases: OrderedDict[str, Case],
        initial_prompt: str = "",
        enable_multiselect: bool = False,
        exclude_ids: set[str] | None = None,
    ):
        super().__init__()

        self.cases = cases
        self.filter_text = initial_prompt
        self.update_task = None
        self.multiselect_enabled = enable_multiselect
        self.marked_case_ids: set[str] = set()
        self.exclude_ids: set[str] = exclude_ids or set()
        self.hide_excluded: bool = True

    @override
    def compose(self):
        with Horizontal():
            yield DataTable[str](
                cursor_type="row", zebra_stripes=True, classes="caselist"
            )
            yield Markdown(classes="preview")
        yield Input(
            self.filter_text, placeholder="Filter", compact=True, select_on_focus=False
        )

    def on_mount(self):
        caselist = self.query_one(DataTable)
        caselist.add_column("SF ID", key="SF ID")
        caselist.add_column("Title", key="Title")
        self._reset_table()
        _ = self.query_one(Input).focus()

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        case_key = event.row_key.value
        preview = self.query_one(Markdown)
        if case_key is None:
            await preview.update("No case selected")
        else:
            case = self.cases[case_key]
            await preview.update(case.preview)

    async def on_input_changed(self, event: Input.Changed):
        self.filter_text = event.value
        if self.update_task is None or self.update_task.done():
            self.update_task = asyncio.create_task(self._update_case_list())

    async def _update_case_list(self):
        await asyncio.sleep(0.1)
        selected = self.selected_case()
        _ = self.query_one(DataTable).clear()

        if self.filter_text is None or self.filter_text == "":
            return self._reset_table()

        return self._apply_filter(self.filter_text, selected)

    def _reset_table(self):
        caselist = self.query_one(DataTable)
        for case in self.cases.values():
            if self._is_excluded(case.sf):
                continue
            _add_row(caselist, case, self._is_marked(case.sf))

    def _apply_filter(self, filter_text: str, selected: Case | None):
        caselist = self.query_one(DataTable)
        for case in self.cases.values():
            if self._is_excluded(case.sf):
                continue
            score = (
                partial_ratio(
                    " ".join([case.sf, case.lp, case.title, case.desc]),
                    filter_text,
                    processor=utils.default_process,
                )
                / 100.0
            )
            if score > 0.8:
                _add_row(caselist, case, self._is_marked(case.sf))
                if selected is not None and case == selected:
                    caselist.move_cursor(row=caselist.get_row_index(selected.sf))
        if selected is None:
            caselist.move_cursor(row=0)

    def _is_excluded(self, case_key: str) -> bool:
        return self.hide_excluded and str(case_key) in self.exclude_ids

    def _is_marked(self, case_key: str) -> bool:
        return self.multiselect_enabled and str(case_key) in self.marked_case_ids

    def _update_row_style(self, case_key: str) -> None:
        caselist = self.query_one(DataTable)
        case = self.cases[case_key]
        marked = self._is_marked(case_key)
        caselist.update_cell(case_key, "SF ID", _styled_text(case.sf, marked))
        caselist.update_cell(case_key, "Title", _styled_text(case.title, marked))

    def selected_case(self) -> Case | None:
        caselist = self.query_one(DataTable)
        if caselist.row_count == 0:
            return None
        # Typechecker doesn't know that Reactive[T] casts to T
        # noinspection PyTypeChecker
        if (
            case_key := caselist.coordinate_to_cell_key(
                caselist.cursor_coordinate
            ).row_key.value
        ) is not None:
            return self.cases.get(case_key)

    def action_cursor_up(self):
        self.query_one(DataTable).action_cursor_up()

    def action_cursor_down(self):
        self.query_one(DataTable).action_cursor_down()

    def action_select_row(self):
        if not self.multiselect_enabled:
            if case := self.selected_case():
                self.post_message(self.CaseSelected(case))
            return

        if self.marked_case_ids:
            cases = [
                case
                for case in self.cases.values()
                if str(case.sf) in self.marked_case_ids
            ]
        else:
            cases = [case] if (case := self.selected_case()) else []

        self.post_message(self.CasesSubmitted(cases))

    def action_toggle_mark(self):
        if not self.multiselect_enabled:
            return

        case = self.selected_case()
        if case is None:
            return

        case_key = str(case.sf)
        if case_key in self.marked_case_ids:
            self.marked_case_ids.remove(case_key)
        else:
            self.marked_case_ids.add(case_key)

        self._update_row_style(case_key)

    def action_toggle_exclude(self):
        if not self.exclude_ids:
            return

        # Preserve currently selected case (if any) so we can restore the cursor
        selected = self.selected_case()
        selected_key = str(selected.sf) if selected is not None else None

        self.hide_excluded = not self.hide_excluded
        table = self.query_one(DataTable)
        _ = table.clear()
        if self.filter_text:
            self._apply_filter(self.filter_text, None)
        else:
            self._reset_table()

        # Restore cursor to the previously selected case if it is still visible
        if selected_key is not None and table.row_count:
            try:
                row_index = table.get_row_index(selected_key)
            except KeyError:
                # The previously selected case is no longer present (e.g. excluded/filtered out)
                return

            # Keep the current column if possible, otherwise default to the first column
            column_index = (
                table.cursor_coordinate.column
                if len(table.columns) > 0 and table.cursor_coordinate is not None
                else 0
            )
            table.move_cursor(row=row_index, column=column_index)

    def check_action(self, action: str, parameters: object) -> bool | None:
        if action == "toggle_mark":
            return self.multiselect_enabled
        if action == "toggle_exclude":
            return bool(self.exclude_ids)
        return True


def _styled_text(content: str, marked: bool) -> Text:
    style = "bold green" if marked else ""
    return Text(content, style=style)


def _add_row(table: DataTable, case: Case, marked: bool) -> None:
    _ = table.add_row(
        _styled_text(case.sf, marked),
        _styled_text(case.title, marked),
        key=str(case.sf),
    )
