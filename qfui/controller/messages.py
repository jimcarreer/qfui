from abc import ABC, abstractmethod, ABCMeta
from typing import List, Optional, Dict

from PySide6.QtCore import QObject

from qfui.models.layers import GridLayer
from qfui.models.project import Project, SectionLayerIndex
from qfui.models.sections import Section, SectionStart
from qfui.utils import QABCMeta


class ControllerInterface(ABC, QObject, metaclass=QABCMeta):

    @property
    @abstractmethod
    def project(self) -> Project:
        pass

    @project.setter
    @abstractmethod
    def project(self, project: Project):
        pass

    @property
    @abstractmethod
    def sections(self) -> List[Section]:
        pass

    @property
    @abstractmethod
    def visible_layers(self) -> Dict[SectionLayerIndex, GridLayer]:
        pass

    @abstractmethod
    def clear_all_visible_layers(self):
        pass

    @abstractmethod
    def set_layers_as_visible(self, visible: List[SectionLayerIndex]):
        pass

    @abstractmethod
    def remove_layers_as_visible(self, remove: List[SectionLayerIndex]):
        pass

    @abstractmethod
    def grid_layer(self, idx: SectionLayerIndex) -> Optional[GridLayer]:
        pass

    @abstractmethod
    def layer_start_position(self, idx: SectionLayerIndex) -> Optional[SectionStart]:
        pass
