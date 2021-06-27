from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from qfui.models.enums import SectionModes
from qfui.models.layers import RawLayer, GridLayer


@dataclass
class SectionStart:

    x: Optional[int] = None
    y: Optional[int] = None
    comment: Optional[str] = None

    def __str__(self):
        if self.x is None and self.y is None and self.comment is None:
            return "Empty"
        ret = f"({self.x}, {self.y})" if self.x and self.y else ""
        ret = f"{ret} {self.comment}" if self.comment else ret
        return ret


@dataclass
class Section:

    mode: SectionModes = None
    label: str = f"{uuid.uuid4()}"
    hidden: bool = False
    start: SectionStart = None
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
