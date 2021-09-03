import logging
import sys
from abc import ABCMeta

from PySide6.QtCore import QObject


def configure_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.handlers = [handler]


class QABCMeta(type(QObject), ABCMeta):
    pass
