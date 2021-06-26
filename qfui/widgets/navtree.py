from __future__ import annotations

import os
from abc import ABC, ABCMeta, abstractmethod
from typing import Any, List, Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt

from qfui.models.sections import Section
from qfui.qfparser.blueprints import Blueprint


class NavigationNode(ABC):

    def __init__(self, parent: Optional[NavigationNode], children: List[NavigationNode]):
        self._parent = parent
        self._children = children

    @property
    @abstractmethod
    def label(self) -> str:
        pass

    @property
    def child_nodes(self) -> List[NavigationNode]:
        return self._children

    @property
    def parent_node(self) -> Optional[NavigationNode]:
        return self._parent

    @property
    def index_in_parent(self) -> int:
        if not self.parent_node:
            return 0
        return self.parent_node.child_nodes.index(self)


class SectionNode(NavigationNode):

    def __init__(self, parent: NavigationNode, section: Section):
        super().__init__(parent, [])
        self._section = section

    @property
    def label(self) -> str:
        return f'{self._section.mode}: (label : {self._section.label})'


class BlueprintNode(NavigationNode):

    def __init__(self, parent: NavigationNode, blueprint: Blueprint):
        children = [SectionNode(self, s) for s in blueprint.sections]
        super().__init__(parent, children)
        self._blueprint = blueprint

    @property
    def label(self) -> str:
        return os.path.basename(self._blueprint.filepath)


class RootNode(NavigationNode):

    def label(self) -> str:
        return self._label

    def __init__(self, blueprints: List[Blueprint]):
        children = [BlueprintNode(self, b) for b in blueprints]
        super().__init__(None, children)
        self._label = '<ROOT>'


class NavigationTree(QAbstractItemModel):

    def __init__(self, blueprints: List[Blueprint]):
        super().__init__()
        self._root = RootNode(blueprints)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['Filename']
        return None

    def columnCount(self, _: QModelIndex) -> int:
        return 1

    def data(self, index: QModelIndex, role: int) -> Qt.QVariant:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        item: NavigationNode = index.internalPointer()
        return item.label

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent: NavigationNode = self._root if not parent.isValid() else parent.internalPointer()
        child = parent.child_nodes[row] if row < len(parent.child_nodes) else None
        if not child:
            return QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, index: QModelIndex) -> QObject:
        if not index.isValid():
            return QModelIndex()
        child: NavigationNode = index.internalPointer()
        parent: NavigationNode = child.parent_node
        if parent == self._root:
            return QModelIndex()
        return self.createIndex(parent.index_in_parent, 0, parent)

    def rowCount(self, parent: QModelIndex) -> int:
        if parent.column() > 0:
            return 0
        parent: NavigationNode = self._root if not parent.isValid() else parent.internalPointer()
        return len(parent.child_nodes)
