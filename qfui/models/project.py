import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Generator

from qfui.models.layers import GridLayer, Layer
from qfui.models.sections import Section, GridSection


@dataclass(eq=True, frozen=True, order=True)
class SectionLayerIndex:

    section_index: uuid.UUID = None
    layer_index: uuid.UUID = None


@dataclass
class Project:

    # Core Model data
    sections: List[Section] = field(default_factory=list)
    # ViewModel Like data
    visible_layers: List[SectionLayerIndex] = field(default_factory=list)
    active_layer: SectionLayerIndex = None

    def __post_init__(self):
        self._section_lookup = {}
        self._section_layer_lookup = {}
        for s in self.sections:
            self._section_lookup[s.suid] = s
            if not isinstance(s, GridSection):
                continue
            self._section_layer_lookup.update({
                SectionLayerIndex(s.suid, layer.luid): layer
                for layer in s.layers
            })

    def get_grid_layer(self, section_layer_id: SectionLayerIndex) -> Optional[GridLayer]:
        return self._section_layer_lookup.get(section_layer_id, None)

    def find_layers(self, filter_fn: Callable[[SectionLayerIndex, Layer], bool]) -> Generator:
        for layer_idx, layer in self._section_layer_lookup.items():
            if not filter_fn(layer_idx, layer):
                continue
            yield layer_idx, layer
