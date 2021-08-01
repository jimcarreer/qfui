from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Set

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QSortFilterProxyModel, Signal, Slot
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QTreeView, QToolBar, QVBoxLayout, QLineEdit, QLabel, QMenu

from qfui.controller.messages import ControllerInterface
from qfui.models.enums import SectionModes
from qfui.models.layers import GridLayer
from qfui.models.sections import Section, GridSection
from qfui.models.project import SectionLayerIndex
from qfui.utils import QABCMeta
from qfui.widgets.modes import ModeSelectionDialog


class Node(ABC, QObject, metaclass=QABCMeta):

    @property
    @abstractmethod
    def tree_label(self) -> str:
        pass

    @property
    @abstractmethod
    def child_nodes(self) -> List[SimpleNode]:
        pass

    @property
    @abstractmethod
    def parent_node(self) -> Optional[SimpleNode]:
        pass

    @parent_node.setter
    def parent_node(self, parent: Optional[SimpleNode]):
        pass

    @property
    @abstractmethod
    def index_in_parent(self) -> int:
        pass


class SimpleNode(Node, metaclass=QABCMeta):

    def __init__(self, parent: Optional[Node], children: List[Node]):
        super().__init__()
        self._parent = parent
        self._children = children

    @property
    @abstractmethod
    def tree_label(self) -> str:
        pass

    @property
    def child_nodes(self) -> List[Node]:
        return self._children

    @property
    def parent_node(self) -> Optional[SimpleNode]:
        return self._parent

    @parent_node.setter
    def parent_node(self, parent: Optional[SimpleNode]):
        self._parent = parent

    @property
    def index_in_parent(self) -> int:
        if not self.parent_node:
            return 0
        return self.parent_node.child_nodes.index(self)


class GroupNode(SimpleNode):

    def __init__(self, parent: SimpleNode, name: str, children: List[SimpleNode]):
        for child in children:
            child.parent_node = self
        super().__init__(parent, children)
        self._name = name

    @property
    def tree_label(self) -> str:
        return self._name


class PropertyNode(SimpleNode):

    def __init__(self, parent: SimpleNode, name: str, value: str):
        super().__init__(parent, [])
        self._name = name
        self._value = value

    @property
    def tree_label(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value


class LayerNode(SimpleNode):

    def __init__(self, label: str, parent: Node, section_layer_index: SectionLayerIndex, layer: GridLayer):
        self._section_layer_idx = section_layer_index
        self._tree_label = label
        children = [
            PropertyNode(self, self.tr("Relative Z"), str(layer.relative_z)),
            PropertyNode(self, self.tr("Width"), str(layer.width)),
            PropertyNode(self, self.tr("Height"), str(layer.height)),
            PropertyNode(self, self.tr("Visible"), str(layer.visible)),
            PropertyNode(self, self.tr("Editable"), str(layer.active))
        ]
        super().__init__(parent, children)

    @property
    def tree_label(self) -> str:
        return self._tree_label

    @property
    def section_layer_index(self) -> SectionLayerIndex:
        return self._section_layer_idx


class SectionNode(SimpleNode):

    def __init__(self, parent: Optional[SimpleNode], section_idx: int, section: Section, active_only: bool = False):
        self._section_idx = section_idx
        self._section_mode = section.mode
        self._section_label = section.label
        self._section_comment = section.comment
        self._has_active_layer = False
        self._active_only = active_only
        children = [
            PropertyNode(self, self.tr("Mode"), section.mode.value),
            PropertyNode(self, self.tr("Label"), section.label)
        ]
        if section.start:
            children.append(PropertyNode(self, self.tr("Start"), str(section.start)))
        if section.mode == SectionModes.DIG:
            section: GridSection = section
            prefix = self.tr("Layer")
            children += [
                LayerNode(f"{prefix} {lidx:03d}", self, SectionLayerIndex(section.suuid, layer.luuid), layer)
                for lidx, layer in enumerate(section.layers)
                if not self._active_only or layer.active or layer.visible
            ]
            self._has_active_layer = any(layer.active or layer.visible for layer in section.layers)
        super().__init__(parent, children)

    @property
    def has_active_layer(self) -> bool:
        return self._has_active_layer

    @property
    def mode(self) -> SectionModes:
        return self._section_mode

    @property
    def section_idx(self) -> int:
        return self._section_idx

    @property
    def tree_label(self) -> str:
        return f"{self._section_idx:03d} - {self._section_label}"

    @property
    def comment(self) -> str:
        return self._section_comment


class RootNode(Node):

    @property
    def index_in_parent(self) -> int:
        return -1

    @property
    def parent_node(self) -> Optional[SimpleNode]:
        return None

    def __init__(self, controller: ControllerInterface = None):
        super().__init__()
        self._sections_node = GroupNode(self, self.tr("Sections"), [])
        self._active_node = GroupNode(self, self.tr("Active Layers"), [])
        self._layer_lookup = {}
        self.init_from_controller(controller)

    def init_from_controller(self, controller: ControllerInterface):
        if not controller:
            return
        sections_children = []
        active_section_children = []
        for sidx, section in enumerate(controller.sections):
            sections_children.append(SectionNode(None, sidx, section))
            if sections_children[-1].has_active_layer:
                active_section_children.append(SectionNode(None, sidx, section, True))
        self._sections_node = GroupNode(self, self.tr("Sections"), sections_children)
        self._active_node = GroupNode(self, self.tr("Active Layers"), active_section_children)

    @property
    def child_nodes(self) -> List[SimpleNode]:
        return [self._active_node, self._sections_node]

    @property
    def tree_label(self) -> str:
        return ""


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

    def __init__(self, controller: Optional[ControllerInterface] = None):
        super().__init__()
        self._root = RootNode() if not controller else RootNode(controller)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        return self.tr("Property") if section == 0 else self.tr("Details")

    def columnCount(self, _: QModelIndex) -> int:
        return 2

    def data(self, index: QModelIndex, role: int) -> Qt.QVariant:
        if not index.isValid() or role not in [Qt.DisplayRole, Qt.UserRole]:
            return None
        item: SimpleNode = index.internalPointer()
        if role == Qt.UserRole:
            return item
        data = [item.tree_label, ""]
        if isinstance(item, PropertyNode):
            data[1] = item.value
        if isinstance(item, SectionNode):
            data[1] = item.comment
        return data[index.column()]

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent: SimpleNode = self._root if not parent.isValid() else parent.internalPointer()
        child = parent.child_nodes[row] if row < len(parent.child_nodes) else None
        if not child:
            return QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, index: QModelIndex) -> QObject:
        if not index.isValid():
            return QModelIndex()
        child: SimpleNode = index.internalPointer()
        parent: SimpleNode = child.parent_node
        if parent == self._root:
            return QModelIndex()
        return self.createIndex(parent.index_in_parent, 0, parent)

    def rowCount(self, parent: QModelIndex) -> int:
        if parent.column() > 0:
            return 0
        parent: SimpleNode = self._root if not parent.isValid() else parent.internalPointer()
        return len(parent.child_nodes)

    def reinitialize(self, controller: ControllerInterface):
        self._root = RootNode(controller)


class NavigationWidget(QWidget):

    layers_set_as_visible = Signal(list)
    remove_layers_as_visible = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._default_mode_filters = set([m for m in SectionModes if m != SectionModes.IGNORE])
        self._layout = QVBoxLayout(parent=self)
        self.setMinimumWidth(450)
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
        self._filter_dialog.ok_clicked.connect(self._update_filters)

    def _init_tree(self):
        self._tree_view = QTreeView(parent=self)
        self._tree_model = NavigationTree()
        self._tree_model_filter = NavigationTreeFilter()
        self._tree_model_filter.allowed_modes = self._default_mode_filters
        self._tree_model_filter.setSourceModel(self._tree_model)
        self._tree_view.setModel(self._tree_model_filter)
        self._tree_view.setColumnWidth(0, 250)
        self._layout.addWidget(self._tree_view)
        self._filter_dialog.selected = self._tree_model_filter.allowed_modes
        self._tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)

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

    def _show_tree_context_menu(self, position):
        selected = self._tree_view.selectedIndexes() or None
        if not selected:
            return
        index: QModelIndex = selected[0]
        node = index.data(Qt.UserRole)
        if not isinstance(node, LayerNode):
            return
        menu = QMenu()
        action = QAction(self.tr("Set visible"))
        action.triggered.connect(lambda: self.layers_set_as_visible.emit([node.section_layer_index]))
        menu.addAction(action)
        action2 = QAction(self.tr("Set invisible"))
        action2.triggered.connect(lambda: self.remove_layers_as_visible.emit([node.section_layer_index]))
        menu.addAction(action2)
        menu.exec(self._tree_view.viewport().mapToGlobal(position))

    @Slot(ControllerInterface)
    def project_changed(self, controller: ControllerInterface):
        self._tree_model_filter.beginResetModel()
        self._tree_model.reinitialize(controller)
        self._tree_model_filter.endResetModel()
        self._tree_view.expandToDepth(0)

    @Slot(ControllerInterface, list, list)
    def layer_visibility_changed(self, controller: ControllerInterface, **kwargs):
        self._tree_model_filter.beginResetModel()
        self._tree_model.reinitialize(controller)
        self._tree_model_filter.endResetModel()
        self._tree_view.expandToDepth(0)
