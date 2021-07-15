from typing import Optional, List

from PySide6.QtCore import Signal

from qfui.controller.messages import ControllerInterface
from qfui.models.layers import GridLayer
from qfui.models.project import Project, SectionLayerIndex
from qfui.models.sections import Section, GridSection


class ProjectController(ControllerInterface):

    project_changed = Signal(ControllerInterface)
    layer_visibility_changed = Signal(ControllerInterface, list)

    def __init__(self, project: Optional[Project] = None):
        super().__init__()
        self._project = project or Project()

    @property
    def project(self) -> Project:
        return self._project

    @project.setter
    def project(self, project: Project):
        self._project = project
        self.project_changed.emit(self)

    @property
    def sections(self) -> List[Section]:
        return self._project.sections

    @property
    def visible_layers(self) -> List[SectionLayerIndex]:
        return self._project.visible_layers

    def _update_visible_layers(self, layer_indexes: List[SectionLayerIndex], remove: bool = False) -> bool:
        modified = False
        for idx in layer_indexes:
            if not remove and idx in self.project.visible_layers:
                continue
            elif remove and idx not in self.project.visible_layers:
                continue
            modified = True
            if remove:
                self.project.visible_layers.remove(idx)
            else:
                self.project.visible_layers.append(idx)
        return modified

    def clear_all_visible_layers(self):
        if not self.project.visible_layers:
            return
        self.project.visible_layers.clear()
        self.layer_visibility_changed.emit(self, [])

    def set_layers_as_visible(self, visible: List[SectionLayerIndex]):
        if self._update_visible_layers(visible):
            self.layer_visibility_changed.emit(self, self.project.visible_layers)

    def remove_layers_as_visible(self, remove: List[SectionLayerIndex]):
        if self._update_visible_layers(remove, True):
            self.layer_visibility_changed.emit(self, self.project.visible_layers)

    def grid_layer(self, idx: SectionLayerIndex) -> Optional[GridLayer]:
        if idx.section_index >= len(self.project.sections):
            return None
        section = self._project.sections[idx.section_index]
        if not isinstance(section, GridSection):
            return None
        if idx.layer_index >= len(section.layers):
            return None
        return section.layers[idx.layer_index]
