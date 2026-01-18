import csv
from collections.abc import Iterable
from pathlib import Path

from .cases import Case


class SalesforceCSV:
    """Salesforce CSV importer

    Selectively import cases from a CSV export of a Salesforce report.
    """

    REQUIRED_COLUMNS = ("Case Number", "Subject", "Description")

    def __init__(self, csv_file: Path, case_dir: Path):
        self.csv_file = csv_file
        self.case_dir = case_dir

    def _validate_headers(self, fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file is missing a header row.")
        missing = [
            column for column in self.REQUIRED_COLUMNS if column not in fieldnames
        ]
        if missing:
            raise ValueError(
                f"CSV file is missing required column(s): {', '.join(missing)}"
            )

    def _validate_row(self, row: dict[str, str], line_number: int) -> dict[str, str]:
        normalized: dict[str, str] = {}
        missing_values: list[str] = []
        for column in self.REQUIRED_COLUMNS:
            value = row.get(column)
            sanitized = value.strip() if isinstance(value, str) else ""
            if not sanitized:
                missing_values.append(column)
            else:
                normalized[column] = sanitized
        if missing_values:
            raise ValueError(
                f"Row {line_number} is missing value(s) for: {', '.join(missing_values)}"
            )
        return normalized

    def cases(self) -> Iterable[Case]:
        with open(self.csv_file) as f:
            reader = csv.DictReader(f)
            self._validate_headers(reader.fieldnames)
            for line_number, row in enumerate(reader, start=2):
                normalized = self._validate_row(row, line_number)
                yield Case(
                    sf=normalized["Case Number"],
                    path=self.case_dir / normalized["Case Number"],
                    title=normalized["Subject"],
                    desc=normalized["Description"],
                )
