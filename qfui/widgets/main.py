from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QGraphicsView, QDockWidget, QFileDialog

from qfui.qfparser.importers import CSVImporter
from qfui.controller import ProjectController
from qfui.widgets.navigation import NavigationWidget


class MainWindow(QMainWindow):

    def __init__(self, project: Optional[ProjectController] = None):
        super().__init__()
        self._project: Optional[ProjectController] = None
        # Place holder for GridView
        self.setCentralWidget(QGraphicsView())
        self.setWindowTitle(self.tr("Quick Fort Designer"))
        self._init_actions()
        self._init_menus()
        self._init_docks()
        self.set_project(project)

    def set_project(self, project: Optional[ProjectController] = None):
        self._project = project
        self._navigation.widget().set_project(self._project)

    def _import_handler(self):
        if not self._import_dialog.exec_():
            return
        file = self._import_dialog.selectedFiles()[0]
        importer = CSVImporter()
        self.set_project(ProjectController(importer.load(file)))

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
        self._navigation.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self._navigation)
