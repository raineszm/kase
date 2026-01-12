import csv
from collections.abc import Iterable
from pathlib import Path

from .cases import Case


class SalesforceCSV:
    """Salesforce CSV importer

    Selectively import cases from a CSV export of a Salesforce report.
    """

    def __init__(self, csv_file: Path, case_dir: Path):
        self.csv_file = csv_file
        self.case_dir = case_dir

    def cases(self) -> Iterable[Case]:
        with open(self.csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield Case(
                    sf=row["Case Number"],
                    path=self.case_dir / row["Case Number"],
                    title=row["Subject"],
                    desc=row["Description"],
                )
