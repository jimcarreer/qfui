from typing import Optional, List, Tuple, Dict

from PySide6.QtCore import Signal

from qfui.controller.messages import ControllerInterface
from qfui.models.layers import GridLayer
from qfui.models.project import Project, SectionLayerIndex
from qfui.models.sections import Section, GridSection, SectionStart


class ProjectController(ControllerInterface):

    project_changed = Signal(ControllerInterface)
    layer_visibility_changed = Signal(ControllerInterface, list, list)

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
    def visible_layers(self) -> Dict[SectionLayerIndex, GridLayer]:
        return {i: l for i, l in self._project.find_layers(lambda i, l: l.visible)}

    def _update_visible_layers(self, layer_indexes: List[SectionLayerIndex], remove: bool = False) -> list:
        modified = []
        for idx in layer_indexes:
            if not (layer := self._project.get_grid_layer(idx)):
                continue  # TODO: Log warn about this
            if (layer.visible and not remove) or (not layer.visible and remove):
                continue
            modified.append(idx)
            layer.visible = False if remove else True
        return modified

    def clear_all_visible_layers(self):
        if not self.project.visible_layers:
            return
        removed = [i for i in self.project.visible_layers]
        self.project.visible_layers.clear()
        self.layer_visibility_changed.emit(self, removed, [])

    def set_layers_as_visible(self, visible: List[SectionLayerIndex]):
        if added := self._update_visible_layers(visible):
            self.layer_visibility_changed.emit(self, [], added)

    def remove_layers_as_visible(self, remove: List[SectionLayerIndex]):
        if removed := self._update_visible_layers(remove, True):
            self.layer_visibility_changed.emit(self, removed, [])

    def grid_layer(self, idx: SectionLayerIndex) -> Optional[GridLayer]:
        return self._project.get_grid_layer(idx)

    def layer_start_position(self, idx: SectionLayerIndex) -> Optional[SectionStart]:
        if not (section := self._project.get_section(idx.suuid)):
            return None
        return section.start
