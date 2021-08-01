from __future__ import annotations

import uuid
from abc import ABC
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
class Section(ABC):

    suuid: uuid.UUID = None
    mode: SectionModes = None
    label: str = None
    hidden: bool = False
    start: SectionStart = None
    message: str = None
    comment: str = None

    def __setattr__(self, key, value):
        if key == "mode" and self.mode is not None:
            raise AttributeError("mode can only be set at initialization")
        super(Section, self).__setattr__(key, value)

    def __post_init__(self):
        self.suuid = self.suuid or uuid.uuid4()
        self.label = self.label or str(self.suuid)


@dataclass
class RawSection(Section):

    layer: RawLayer = None


@dataclass
class GridSection(Section):

    layers: List[GridLayer] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        # Grid sections without starts get a 0, 0 (aka 1, 1 in lau) start
        if not self.start:
            self.start = SectionStart(0, 0)
        self.start.x = self.start.x or 0
        self.start.y = self.start.y or 0
