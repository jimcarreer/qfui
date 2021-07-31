from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Generator, Tuple

import numpy

from qfui.models.cells import Cell


@dataclass
class Layer(ABC):

    luid: uuid.UUID = None

    def __post_init__(self):
        self.luid = self.luid or uuid.uuid4()


@dataclass
class RawLayer(Layer):

    raw_lines: List[List[str]] = field(default_factory=list)


@dataclass
class GridLayer(Layer):

    height: int = None
    width: int = None
    cells: numpy.ndarray = None
    relative_z: int = 0
    visible: bool = False
    active: bool = False

    def __setattr__(self, key, value):
        if key in ("height", "width", "cells") and self.__getattribute__(key) is not None:
            raise AttributeError(f"{key} cannot be set")
        super(GridLayer, self).__setattr__(key, value)

    def __post_init__(self):
        super().__post_init__()
        self.width = self.cells.shape[0]
        self.height = self.cells.shape[1]

    def walk(self, filter_check: callable) -> Generator[Tuple[int, int, Cell], None, None]:
        for (x, y), cell in numpy.ndenumerate(self.cells):
            if not filter_check(x, y, cell):
                continue
            yield (x, y), cell
