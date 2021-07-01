from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Set, Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QSortFilterProxyModel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QTreeView, QToolBar, QVBoxLayout, QLineEdit, QLabel

from qfui.controller import ProjectController
from qfui.models.enums import SectionModes
from qfui.models.layers import GridLayer
from qfui.models.sections import Section, GridSection
from qfui.widgets.modes import ModeSelectionDialog


class NavigationNode(ABC):

    def __init__(self, parent: Optional[NavigationNode], children: List[NavigationNode]):
        self._parent = parent
        self._children = children

    @property
    @abstractmethod
    def tree_label(self) -> str:
        pass

    @property
    @abstractmethod
    def data_model(self) -> Any:
        pass

    @property
    def child_nodes(self) -> List[NavigationNode]:
        return self._children

    @property
    def parent_node(self) -> Optional[NavigationNode]:
        return self._parent

    @parent_node.setter
    def parent_node(self, parent: Optional[NavigationNode]):
        self._parent = parent

    @property
    def index_in_parent(self) -> int:
        if not self.parent_node:
            return 0
        return self.parent_node.child_nodes.index(self)


class GroupNode(NavigationNode):

    def __init__(self, parent: NavigationNode, name: str, children: List[NavigationNode]):
        for child in children:
            child.parent_node = self
        super().__init__(parent, children)
        self._name = name

    @property
    def tree_label(self) -> str:
        return self._name

    @property
    def data_model(self) -> Any:
        return self._name


class PropertyNode(NavigationNode):

    def __init__(self, parent: NavigationNode, name: str, value: str):
        super().__init__(parent, [])
        self._name = name
        self._value = value

    @property
    def tree_label(self) -> str:
        return self._name

    @property
    def data_model(self) -> Any:
        return self._value


class LayerNode(NavigationNode):

    def __init__(self, parent: NavigationNode, layer_idx: int, layer: GridLayer):
        self._layer = layer
        self._layer_idx = layer_idx
        children = [
            PropertyNode(self, "Relative Z", str(self._layer.relative_z)),
            PropertyNode(self, "Width", str(self._layer.width)),
            PropertyNode(self, "Height", str(self._layer.height))
        ]
        super().__init__(parent, children)

    @property
    def tree_label(self) -> str:
        return f"Layer #{self._layer_idx:02d}"

    @property
    def data_model(self) -> Any:
        return self._layer


class SectionNode(NavigationNode):

    def __init__(self, parent: NavigationNode, section: Section):
        self._section = section
        children = [
            PropertyNode(self, "mode", self._section.mode.value),
            PropertyNode(self, "label", self._section.label)
        ]
        if self._section.start:
            children.append(PropertyNode(self, "start", str(self._section.start)))
        if self._section.mode == SectionModes.DIG:
            section: GridSection = section
            children += [LayerNode(self, i, l) for i, l in enumerate(section.layers)]
        super().__init__(parent, children)

    @property
    def mode(self) -> SectionModes:
        return self._section.mode

    @property
    def tree_label(self) -> str:
        return f"{self.index_in_parent:03d} - {self._section.label}"

    @property
    def data_model(self) -> Any:
        return self._section


class RootNode(NavigationNode):

    def __init__(self, project: ProjectController = None):
        super().__init__(None, [])
        self._project = None
        self.set_project(project)

    def set_project(self, project: ProjectController):
        self._children = []
        self._project = project
        if not project:
            return
        group_children = [SectionNode(None, s) for s in project.sections]
        group = GroupNode(self, "Sections", group_children)
        self._children = [group]

    @property
    def tree_label(self) -> str:
        return ''

    @property
    def data_model(self) -> Any:
        return ''


class NavigationTreeFilter(QSortFilterProxyModel):

    def __init__(self):
        super().__init__()
        self._allowed_modes = set([s for s in SectionModes if s != SectionModes.IGNORE])
        self._text_search = None

    @property
    def allowed_modes(self):
        return self._allowed_modes

    @allowed_modes.setter
    def allowed_modes(self, modes: Set[SectionModes] = None):
        self._allowed_modes = modes or set()

    def set_search_text(self, text: str = None):
        text = text.strip()
        self._text_search = text or None

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not source_parent.isValid():
            return True
        parent_node = source_parent.internalPointer()
        if not isinstance(parent_node, GroupNode):
            return True
        child: SectionNode = parent_node.child_nodes[source_row]
        text_matches = True
        if self._text_search is not None:
            text_matches = self._text_search in child.tree_label
        return text_matches and child.mode in self._allowed_modes


class NavigationTree(QAbstractItemModel):

    def __init__(self, project: Optional[ProjectController] = None):
        super().__init__()
        self._project = project
        self._root = RootNode(project)

    def set_project(self, project: Optional[ProjectController] = None):
        self.beginResetModel()
        self._project = project
        self._root.set_project(project)
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        return self.tr("Property") if section == 0 else self.tr("Details")

    def columnCount(self, _: QModelIndex) -> int:
        return 2

    def data(self, index: QModelIndex, role: int) -> Qt.QVariant:
        if not index.isValid() or role not in [Qt.DisplayRole, Qt.UserRole]:
            return None
        item: NavigationNode = index.internalPointer()
        if role == Qt.UserRole:
            return item.data_model
        data = [item.tree_label, '']
        if isinstance(item, PropertyNode):
            data[1] = item.data_model
        if isinstance(item, SectionNode):
            data[1] = item.data_model.comment
        return data[index.column()]

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


class NavigationWidget(QWidget):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._default_mode_filters = set([m for m in SectionModes if m != SectionModes.IGNORE])
        self._layout = QVBoxLayout(parent=self)
        self.setMinimumWidth(600)
        self.setMinimumHeight(150)
        self.setLayout(self._layout)
        self._init_toolbar()
        self._init_tree()

    def _init_toolbar(self):
        self._toolbar = QToolBar(parent=self)
        self._toolbar_search = QLineEdit()
        self._toolbar_search.setPlaceholderText(self.tr("Section label"))
        self._toolbar_search.setFixedWidth(150)
        self._toolbar.addAction(
            QIcon("icons:filter_1x24dp.png"),
            self.tr("Section mode filters"),
            self._show_filter_dialog,
        )
        self._toolbar.addWidget(QLabel(f"{self.tr('Search')}: "))
        self._toolbar.addWidget(self._toolbar_search)
        self._toolbar.addAction(
            QIcon("icons:cancel_1x24dp.png"),
            self.tr("Clear filters"),
            self._clear_filters,
        )
        self._layout.addWidget(self._toolbar)
        self._toolbar_search.textChanged.connect(self._update_filters)
        self._filter_dialog = ModeSelectionDialog(
            self.tr("Section Filter"),
            self,
            self._default_mode_filters,
        )
        self._filter_dialog.okClicked.connect(self._update_filters)

    def _init_tree(self):
        self._tree_view = QTreeView(parent=self)
        self._tree_model = NavigationTree(None)
        self._tree_model_filter = NavigationTreeFilter()
        self._tree_model_filter.allowed_modes = self._default_mode_filters
        self._tree_model_filter.setSourceModel(self._tree_model)
        self._tree_view.setModel(self._tree_model_filter)
        self._tree_view.setColumnWidth(0, 250)
        self._layout.addWidget(self._tree_view)
        self._filter_dialog.selected = self._tree_model_filter.allowed_modes
        self._tree_view.doubleClicked.connect(self._tree_double_click)

    def _clear_filters(self):
        self._tree_model_filter.beginResetModel()
        self._tree_model_filter.set_search_text("")
        self._toolbar_search.setText("")
        self._tree_model_filter.allowed_modes = self._default_mode_filters
        self._filter_dialog.selected = self._default_mode_filters
        self._tree_model_filter.endResetModel()
        self._tree_view.expandToDepth(0)

    def _update_filters(self):
        self._tree_model_filter.beginResetModel()
        self._tree_model_filter.set_search_text(self._toolbar_search.text())
        self._tree_model_filter.allowed_modes = self._filter_dialog.selected
        self._tree_model_filter.endResetModel()
        self._tree_view.expandToDepth(0)

    def _show_filter_dialog(self):
        self._filter_dialog.show()
        self._filter_dialog.setFixedSize(self._filter_dialog.width(), self._filter_dialog.height())

    def set_project(self, project: ProjectController):
        self._tree_model.set_project(project)

    def _tree_double_click(self):
        # TODO: We need signals, we probably also need a proper controller instead of
        #       blueprints in the tree view
        selected = self._tree_view.selectedIndexes() or None
        if not selected:
            return
        index: QModelIndex = selected[0]
        data_model = index.model().data(index, Qt.UserRole)
        if isinstance(data_model, GridLayer):
            print("TODO: Trigger a signal for layer selected")
            pass
