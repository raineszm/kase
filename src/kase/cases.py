import json
import os
import re
import textwrap
from collections.abc import Iterable
from glob import glob
from pathlib import Path

from pydantic import BaseModel


class Case(BaseModel):
    path: Path
    title: str
    desc: str
    sf: str
    lp: str = ""

    def write_metadata(self, clobber=False) -> bool:
        # Check if case.json already exists - don't overwrite
        metadata = self.model_dump()
        path = metadata.pop("path")

        metadata_file = path / "case.json"
        if metadata_file.exists() and not clobber:
            return False
        # Create directory if it doesn't exist
        if not path.exists():
            path.mkdir()
        with metadata_file.open("w") as f:
            json.dump(metadata, f, indent=4)
        return True

    @classmethod
    def from_folder(cls, folder: Path) -> "Case":
        with (folder / "case.json").open("r") as f:
            data = json.load(f)
            return cls(path=folder, **data)

    @property
    def preview(self) -> str:
        return textwrap.dedent(
            """
            # [{sf}] {title}

            {desc}
            """
        ).format(sf=self.sf, title=self.title, desc=self.desc)


class CaseRepo:
    TITLE_RE = re.compile(r"^\[(?P<sf>\d+)\] (?P<title>.+)$")

    def __init__(self, case_dir: str):
        self.case_dir: str = os.path.expanduser(case_dir)

    @property
    def metadata(self) -> list[Path]:
        return [Path(f) for f in glob(f"{self.case_dir}/*/case.json")]

    @property
    def cases(self) -> Iterable[Case]:
        for meta in self.metadata:
            yield self._load_meta(meta)

    @staticmethod
    def _load_meta(meta: Path) -> Case:
        with meta.open("r") as f:
            data = json.load(f)
            return Case(path=meta.parent, **data)

    def open_case(self, case_folder: Path) -> Case:
        return self._load_meta(case_folder / "case.json")

    def create_case(self, name: str, lp: str, description: str) -> bool:
        match = self.TITLE_RE.match(name)
        if not match:
            return False
        sf = match.group("sf")
        title = match.group("title")
        path = Path(self.case_dir) / sf
        case = Case(
            path=path,
            sf=sf,
            title=title,
            desc=description,
        )
        return case.write_metadata(clobber=False)
