import json
import os
from collections.abc import Iterable
from glob import glob
from pathlib import Path
import textwrap


class CaseRepo:
    def __init__(self, case_dir: str):
        self.case_dir: str = os.path.expanduser(case_dir)

    @property
    def metadata(self) -> list[Path]:
        return [Path(f) for f in glob(f"{self.case_dir}/*/case.json")]

    @property
    def rows(self) -> Iterable[dict[str, str]]:
        for meta in self.metadata:
            yield self._load_meta(meta)

    @staticmethod
    def _load_meta(meta: Path) -> dict[str, str]:
        with meta.open("r") as f:
            data = json.load(f)
            data["path"] = str(meta.parent)
            return data

    def case_preview(self, path: str) -> str:
        meta = Path(path) / "case.json"
        data = self._load_meta(meta)
        return textwrap.dedent(
            """# [{sf}] {title}

            {desc}
            """.format(**data)
        )
