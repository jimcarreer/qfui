from typing import Optional, List

from PySide6.QtCore import Signal

from qfui.controller.messages import ControllerInterface, LayerVisibilityChanged
from qfui.models.project import Project
from qfui.models.sections import Section


class ProjectController(ControllerInterface):

    project_changed = Signal(ControllerInterface)
    layer_visibility_changed = Signal(ControllerInterface, LayerVisibilityChanged)

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

    def set_layer_visibility(self, event: LayerVisibilityChanged):
        if not event.visible:
            return
        self._project.visible_layers = []
        self._project.visible_layers.append(event.layer_index)
        self.layer_visibility_changed.emit(self, event)
