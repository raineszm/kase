"""Integration tests for the ImporterApp TUI."""

import csv
import json
from pathlib import Path

from textual.widgets import Footer, Header

from kase.importer import SalesforceCSV
from kase.tui.importer import ImporterApp
from kase.tui.widgets.case_selector import CaseSelector


def write_salesforce_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SalesforceCSV.REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class TestImporterApp:
    """Integration tests covering ImporterApp wiring and events."""

    def test_importer_app_compose_snapshot(self, snap_compare, tmp_path):
        """Ensure ImporterApp composes to the expected widget tree.

        Uses real filesystem because snapshot tests need to write real files.
        """
        case_dir = tmp_path / "cases"
        case_dir.mkdir()
        csv_path = tmp_path / "cases.csv"
        write_salesforce_csv(
            csv_path,
            [
                {
                    "Case Number": "1001",
                    "Subject": "First issue",
                    "Description": "First description",
                }
            ],
        )

        app = ImporterApp(case_dir=case_dir.as_posix(), csv_file=csv_path)
        assert snap_compare(app)

    async def test_importer_app_mounts_core_widgets(self, fs):
        """Verify ImporterApp wires up the header, selector, and footer."""
        case_dir = Path("/cases")
        fs.create_dir(case_dir)
        csv_path = Path("/cases.csv")
        write_salesforce_csv(
            csv_path,
            [
                {
                    "Case Number": "1001",
                    "Subject": "First issue",
                    "Description": "First description",
                }
            ],
        )

        app = ImporterApp(case_dir=case_dir.as_posix(), csv_file=csv_path)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.query_one(Header) is not None
            assert app.query_one(CaseSelector) is not None
            assert app.query_one(Footer) is not None

    async def test_importer_app_excludes_existing_cases(self, fs):
        """Existing case IDs should be excluded from the selection list."""
        case_dir = Path("/cases")
        fs.create_dir(case_dir)
        existing_case_dir = case_dir / "1001"
        fs.create_dir(existing_case_dir)
        fs.create_file(
            existing_case_dir / "case.json",
            contents=json.dumps(
                {
                    "title": "Existing Case",
                    "desc": "Existing description",
                    "sf": "1001",
                    "lp": "",
                }
            ),
        )

        csv_path = Path("/cases.csv")
        write_salesforce_csv(
            csv_path,
            [
                {
                    "Case Number": "1001",
                    "Subject": "Existing case",
                    "Description": "Should be excluded",
                },
                {
                    "Case Number": "1002",
                    "Subject": "New case",
                    "Description": "Should be visible",
                },
            ],
        )

        app = ImporterApp(case_dir=case_dir.as_posix(), csv_file=csv_path)
        async with app.run_test() as pilot:
            await pilot.pause()
            selector = app.query_one(CaseSelector)
            datatable = selector.query_one("DataTable")

            assert datatable.row_count == 1

    def test_cases_submitted_event_exits_app(self, mocker, monkeypatch, fs):
        """Ensure the CasesSubmitted message exits the app with selected cases."""
        case_dir = Path("/cases")
        fs.create_dir(case_dir)
        csv_path = Path("/cases.csv")
        write_salesforce_csv(
            csv_path,
            [
                {
                    "Case Number": "1001",
                    "Subject": "First issue",
                    "Description": "First description",
                }
            ],
        )

        app = ImporterApp(case_dir=case_dir.as_posix(), csv_file=csv_path)
        captured = {}

        def fake_exit(result, *, return_code):
            captured["result"] = result
            captured["return_code"] = return_code

        monkeypatch.setattr(app, "exit", fake_exit)

        mock_case = mocker.MagicMock()
        event = CaseSelector.CasesSubmitted([mock_case])

        app.action_select_rows(event)

        assert captured["result"] == [mock_case]
        assert captured["return_code"] == 0
