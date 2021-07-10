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

    @visible_layers.setter
    def visible_layers(self, visible: List[SectionLayerIndex]):
        self.project.visible_layers = visible
        self.layer_visibility_changed.emit(self, visible)

    def grid_layer(self, idx: SectionLayerIndex) -> Optional[GridLayer]:
        if idx.section_index >= len(self.project.sections):
            return None
        section = self._project.sections[idx.section_index]
        if not isinstance(section, GridSection):
            return None
        if idx.layer_index >= len(section.layers):
            return None
        return section.layers[idx.layer_index]
