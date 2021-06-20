from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List

from qfui.models.enums import SectionModes
from qfui.models.layers import RawLayer, GridLayer


@dataclass
class Section:

    mode: SectionModes = None
    label: str = f"{uuid.uuid4()}"
    hidden: bool = False
    start_x: int = 0
    start_y: int = 0
    start_comment: str = None
    message: str = None
    comment: str = None

    def __setattr__(self, key, value):
        if key == "mode" and self.mode is not None:
            raise AttributeError("mode can only be set at initialization")
        super(Section, self).__setattr__(key, value)


@dataclass
class RawSection(Section):

    layer: RawLayer = None


@dataclass
class GridSection(Section):

    layers: List[GridLayer] = field(default_factory=list)
