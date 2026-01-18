"""Unit tests for the SalesforceCSV importer."""

import csv
from pathlib import Path

import pytest

from kase.cases import Case
from kase.importer import SalesforceCSV


def write_salesforce_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SalesforceCSV.REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_cases_yield_case_objects(tmp_path):
    csv_path = tmp_path / "cases.csv"
    case_dir = tmp_path / "cases"
    case_dir.mkdir()

    write_salesforce_csv(
        csv_path,
        [
            {
                "Case Number": "0001",
                "Subject": "First issue",
                "Description": "First description",
            },
            {
                "Case Number": "0002",
                "Subject": "Second issue",
                "Description": "Second description",
            },
        ],
    )

    importer = SalesforceCSV(csv_path, case_dir)
    cases = list(importer.cases())

    assert len(cases) == 2
    assert [case.sf for case in cases] == ["0001", "0002"]
    assert all(isinstance(case, Case) for case in cases)
    assert cases[0].path == case_dir / "0001"
    assert cases[1].desc == "Second description"


def test_cases_strip_whitespace(tmp_path):
    csv_path = tmp_path / "cases.csv"
    case_dir = tmp_path / "cases"
    case_dir.mkdir()

    write_salesforce_csv(
        csv_path,
        [
            {
                "Case Number": " 0003 ",
                "Subject": "  Spaced subject  ",
                "Description": "  Spaced description  ",
            }
        ],
    )

    importer = SalesforceCSV(csv_path, case_dir)
    case = next(importer.cases())

    assert case.sf == "0003"
    assert case.title == "Spaced subject"
    assert case.desc == "Spaced description"
    assert case.path == case_dir / "0003"


def test_missing_header_row_raises(tmp_path):
    csv_path = tmp_path / "cases.csv"
    case_dir = tmp_path / "cases"
    case_dir.mkdir()

    csv_path.write_text("")

    importer = SalesforceCSV(csv_path, case_dir)

    with pytest.raises(ValueError, match="missing a header row"):
        list(importer.cases())


def test_missing_required_column_in_header(tmp_path):
    csv_path = tmp_path / "cases.csv"
    case_dir = tmp_path / "cases"
    case_dir.mkdir()

    csv_path.write_text("Case Number,Subject\n0001,Missing description\n")

    importer = SalesforceCSV(csv_path, case_dir)

    with pytest.raises(ValueError, match="missing required column"):
        list(importer.cases())


def test_missing_value_in_row_raises(tmp_path):
    csv_path = tmp_path / "cases.csv"
    case_dir = tmp_path / "cases"
    case_dir.mkdir()

    write_salesforce_csv(
        csv_path,
        [
            {
                "Case Number": "0004",
                "Subject": "",
                "Description": "Missing subject",
            }
        ],
    )

    importer = SalesforceCSV(csv_path, case_dir)

    with pytest.raises(
        ValueError,
        match=r"Row 2 is missing value\(s\) for: Subject",
    ):
        list(importer.cases())
