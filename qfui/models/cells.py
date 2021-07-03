from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from qfui.models.enums import Designations


@dataclass
class Cell:

    raw_text: Optional[str] = None
    from_expansion: bool = False


@dataclass
class DesignationCell(Cell):

    designation: Designations = None
    priority: Optional[int] = 4


@dataclass()
class UnprocessedCell(Cell):

    code_text: str = None
