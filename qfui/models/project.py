from dataclasses import dataclass, field
from typing import List

from qfui.models.sections import Section


class SectionLayerIndex:

    section_index: int = None
    layer_index: int = None


@dataclass
class Project:

    # Model data
    sections: List[Section] = field(default_factory=list)
    # ViewModel-ish data
    visible_layers: List[SectionLayerIndex] = field(default_factory=list)
    active_layer: SectionLayerIndex = None
