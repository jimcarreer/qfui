import logging
import sys

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

import qfui.resources
from qfui import sprites
from qfui.utils import configure_logging
from qfui.models.project import Project
from qfui.qfparser.importers import CSVImporter
from qfui.widgets.main import MainWindow


if __name__ == "__main__":
    configure_logging()
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
