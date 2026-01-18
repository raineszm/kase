"""Integration tests for QueryApp TUI."""

import pytest
from textual.widgets import Footer, Header

from kase.tui.query import QueryApp
from kase.tui.widgets.case_selector import CaseSelector


@pytest.fixture
def query_app_test_cases(case_repo_query_small):
    """Provide path to a small, pre-created case repo for QueryApp tests."""
    return case_repo_query_small


class TestQueryApp:
    """Integration tests covering QueryApp wiring and events."""

    def test_query_app_compose_snapshot(self, snap_compare, case_repo_query_small):
        """Ensure QueryApp composes to the expected widget tree."""
        app = QueryApp(case_dir=case_repo_query_small)
        assert snap_compare(app)

    async def test_query_app_mounts_core_widgets(self, query_app_test_cases):
        """Verify QueryApp wires up the header, selector, and footer."""
        app = QueryApp(case_dir=query_app_test_cases)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.query_one(Header) is not None
            assert app.query_one(CaseSelector) is not None
            assert app.query_one(Footer) is not None

    def test_case_selected_event_exits_app(self, mocker, monkeypatch, tmp_path):
        """Ensure the CaseSelected message results in the app exiting with a case."""
        app = QueryApp(case_dir=tmp_path.as_posix())
        captured = {}

        def fake_exit(result, *, return_code):
            captured["result"] = result
            captured["return_code"] = return_code

        monkeypatch.setattr(app, "exit", fake_exit)

        case_path = tmp_path / "chosen_case"
        case_path.mkdir()
        mock_case = mocker.MagicMock()
        mock_case.path = case_path
        event = CaseSelector.CaseSelected(mock_case)

        app.action_select_row(event)

        assert captured["result"] == mock_case
        assert captured["return_code"] == 0
