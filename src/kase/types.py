from typing import TypedDict

from textual._path import CSSPathType
from textual.driver import Driver


class AppOptions(TypedDict, total=False):
    driver_class: type[Driver] | None
    css_path: CSSPathType | None
    watch_css: bool
    ansi_color: bool
