from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from qfui.models.cells import Cell


@dataclass
class RawLayer:

    raw_lines: List[List[str]] = field(default_factory=list)


@dataclass
class GridLayer:

    cells: List[Cell] = field(default_factory=list)
    relative_z: int = 0

    def __post_init__(self):
        self._look_up = {(c.layer_x, c.layer_y): c for c in self.cells}
        self._width = None
        self._height = None
        for x, y in self._look_up:
            self._width = max(self._width, x) if self._width else x
            self._height = max(self._height, y) if self._height else y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
