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

    def write_metadata(self) -> None:
        metadata = self.model_dump()
        path = metadata.pop("path")
        with (path / "case.json").open("w") as f:
            json.dump(metadata, f, indent=4)


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

    def case_preview(self, path: str) -> str:
        meta = Path(path) / "case.json"
        data = self._load_meta(meta)
        return textwrap.dedent(
            """
            # [{sf}] {title}

            {desc}
            """
        ).format(sf=data.sf, title=data.title, desc=data.desc)

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
        # Check if case.json already exists - don't overwrite
        metadata_file = path / "case.json"
        if metadata_file.exists():
            return False
        # Create directory if it doesn't exist
        if not path.exists():
            path.mkdir()
        case.write_metadata()
        return True
