from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QDockWidget, QFileDialog

from qfui.models.layers import GridLayer
from qfui.models.project import Project, SectionLayerIndex
from qfui.qfparser.importers import CSVImporter
from qfui.controller.project import ProjectController
from qfui.widgets.gridview import LayerViewer
from qfui.widgets.navigation import NavigationWidget


class MainWindow(QMainWindow):

    def __init__(self, project: Optional[Project] = None):
        super().__init__()
        self._controller = ProjectController()
        self.setWindowTitle(self.tr("Quick Fort Designer"))
        self._init_actions()
        self._init_menus()
        self._init_docks()
        self._init_centrals()
        if project is not None:
            self._controller.project = project

    def _init_centrals(self):
        self._layer_view = LayerViewer()
        self._controller.layer_visibility_changed.connect(self._layer_view.layer_visibility_changed)
        self._controller.project_changed.connect(self._layer_view.project_changed)
        self.setCentralWidget(self._layer_view)

    def _import_handler(self):
        if not self._import_dialog.exec_():
            return
        file = self._import_dialog.selectedFiles()[0]
        importer = CSVImporter()
        self._controller.project = Project(importer.load(file))

    def _init_actions(self):
        self._import_dialog = QFileDialog(self)
        self._import_dialog.setNameFilter(self.tr("CSV (*.csv)"))
        self._import_dialog.setViewMode(QFileDialog.Detail)
        self._import_action = QAction(self.tr("&Import"), self)
        self._import_action.triggered.connect(self._import_handler)

    def _init_menus(self):
        self._file_menu = self.menuBar().addMenu(self.tr("&File"))
        self._file_menu.addAction(self._import_action)

    def _init_docks(self):
        self._navigation = QDockWidget(self)
        self._navigation.setWidget(NavigationWidget(self))
        self._controller.project_changed.connect(self._navigation.widget().project_changed)
        self._navigation.widget().layer_selected.connect(self._layer_click_handler)
        self._navigation.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self._navigation)

    def _layer_click_handler(self, section_layer_idx: SectionLayerIndex):
        self._controller.visible_layers = [section_layer_idx]
