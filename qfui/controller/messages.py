from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import Slot, QObject

from qfui.models.project import Project, SectionLayerIndex
from qfui.models.sections import Section


@dataclass
class LayerVisibilityChanged:

    layer_index: SectionLayerIndex
    visible: bool


class QABCMeta(type(QObject), ABCMeta):
    pass


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

    @abstractmethod
    @Slot(SectionLayerIndex, bool)
    def set_layer_visibility(self, event: LayerVisibilityChanged):
        pass
