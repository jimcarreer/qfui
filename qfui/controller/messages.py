from abc import ABC, abstractmethod, ABCMeta
from typing import List, Optional

from PySide6.QtCore import QObject

from qfui.models.layers import GridLayer
from qfui.models.project import Project, SectionLayerIndex
from qfui.models.sections import Section
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
    def visible_layers(self) -> List[SectionLayerIndex]:
        pass

    @visible_layers.setter
    @abstractmethod
    def visible_layers(self, visible: List[SectionLayerIndex]) -> List[SectionLayerIndex]:
        pass

    @abstractmethod
    def grid_layer(self, idx: SectionLayerIndex) -> Optional[GridLayer]:
        pass
