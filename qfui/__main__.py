import sys

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

import qfui.resources
from qfui.models.project import Project
from qfui.qfparser.importers import CSVImporter
from qfui.widgets.main import MainWindow
from qfui import sprites

if __name__ == "__main__":
    qfui.resources.initialize()
    sprites.initialize(QImage("sprites:defaults.png"))
    app = QApplication(sys.argv)
    importer = CSVImporter()
    project = Project(importer.load("../tests/data/dreamfort.csv"))
    main_win = MainWindow(project)
    geo = main_win.screen().availableGeometry()
    main_win.resize(geo.width(), geo.height())
    main_win.show()
    sys.exit(app.exec())
