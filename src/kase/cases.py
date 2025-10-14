import json
import os
from collections.abc import Iterable
from glob import glob
from pathlib import Path


class CaseRepo:
    def __init__(self, case_dir: str):
        self.case_dir: str = os.path.expanduser(case_dir)

    @property
    def metadata(self) -> list[Path]:
        return [Path(f) for f in glob(f"{self.case_dir}/*/case.json")]

    @property
    def rows(self) -> Iterable[dict[str, str]]:
        for meta in self.metadata:
            with meta.open("r") as f:
                data = json.load(f)
                data["path"] = str(meta.parent)
                yield data
