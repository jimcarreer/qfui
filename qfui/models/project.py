from dataclasses import dataclass, field
from typing import List

from qfui.models.sections import Section


@dataclass(eq=True, frozen=True, order=True)
class SectionLayerIndex:

    section_index: int = None
    layer_index: int = None


@dataclass
class Project:

    # Core Model data
    sections: List[Section] = field(default_factory=list)
    # ViewModel Like data
    visible_layers: List[SectionLayerIndex] = field(default_factory=list)
    active_layer: SectionLayerIndex = None
