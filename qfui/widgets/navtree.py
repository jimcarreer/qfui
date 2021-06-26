from __future__ import annotations

import os
from abc import ABC, ABCMeta, abstractmethod
from typing import Any, List, Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt

from qfui.models.sections import Section
from qfui.qfparser.blueprints import Blueprint


class NavigationItemMetaClass(ABCMeta, type(QAbstractItemModel)):
    pass


class NavigationItem(ABC, metaclass=NavigationItemMetaClass):

    def __init__(self, parent: Optional[NavigationItem] = None, children: Optional[List[NavigationItem]] = None):
        super().__init__()
        self._parent = parent
        self._children = children or []

    @property
    def child_items(self) -> List[NavigationItem]:
        return self._children

    @property
    def parent_item(self) -> Optional[NavigationItem]:
        return self._parent

    def __repr__(self):
        return f'{self.tree_label}({super().__repr__()})'

    @property
    @abstractmethod
    def tree_label(self) -> str:
        pass

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        print(f'Asking for index for {row}, {column}, {parent} in {self.tree_label}')
        if not self.hasIndex(row, column, parent):
            print(f'Return empty {self.tree_label}')
            return QModelIndex()
        parent: NavigationItem = self if not parent.isValid() else parent.internalPointer()
        if row < len(parent.child_items):
            print(f'Return index {self.tree_label}: {parent.child_items[row]}')
            return self.createIndex(row, column, parent.child_items[row])
        print(f'Return final empty {self.tree_label}')
        return QModelIndex()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.child_items)

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def parent(self, index: QModelIndex) -> QModelIndex:
        print(f'Asking for parent for {index} in {self.tree_label}')
        if not index.isValid():
            return QModelIndex()
        child: NavigationItem = index.internalPointer()
        parent = child.parent_item
        if parent is None:
            return QModelIndex()
        return self.createIndex(index.row(), 0, parent)

    def data(self, index: QModelIndex, role: int) -> Qt.QVariant:
        print(f'Asking for data for {index} in {self.tree_label}')
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self._children[index.row()].tree_label


class NavigationTree(NavigationItem, QAbstractItemModel):

    @property
    def tree_label(self) -> str:
        return 'ROOT'

    def __init__(self, blueprints: List[Blueprint]):
        children = [BlueprintItem(self, bp) for bp in blueprints]
        super().__init__(None, children)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['Filename']
        return None


class BlueprintItem(NavigationItem, QAbstractItemModel):

    @property
    def tree_label(self) -> str:
        return os.path.basename(self._bp.filepath)

    def __init__(self, parent: NavigationTree, blueprint: Blueprint):
        children = [SectionItem(self, s) for s in blueprint.sections]
        super().__init__(parent, children)
        self._bp = blueprint


class SectionItem(NavigationItem, QAbstractItemModel):

    @property
    def tree_label(self) -> str:
        return self._section.label

    def __init__(self, parent: BlueprintItem, section: Section):
        super().__init__()
        self._parent = parent
        self._section = section


class LayerItem(QAbstractItemModel):
    pass
