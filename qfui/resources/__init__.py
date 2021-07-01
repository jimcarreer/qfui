import sys
import importlib.resources

from PySide6 import QtCore

__RESOURCE_DIRS__ = ["icons"]


def initialize():

    for res_dir in __RESOURCE_DIRS__:
        with importlib.resources.path(sys.modules[__name__], res_dir) as path:
            QtCore.QDir.addSearchPath(res_dir, str(path))
