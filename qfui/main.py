import math
import sys
from typing import Optional, Generator, Tuple, List

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QMouseEvent, QPen, Qt, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem, QApplication, QGraphicsView, QGraphicsScene, QStyleOptionGraphicsItem, QWidget, QMainWindow
)


CELL_PX_SIZE = 20
CELL_BORDER_PX_SIZE = 1


class DesignationCell(QGraphicsItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self, cell_x: int, cell_y: int):
        super().__init__()
        self._cell_x = cell_x
        self._cell_y = cell_y
        self._color = QColor(255, 0, 0, 255)

    @property
    def alpha(self) -> int:
        return self._color.alpha()

    @alpha.setter
    def alpha(self, alpha: int):
        self._color.setAlpha(alpha)

    def type(self) -> int:
        return DesignationCell.QT_TYPE

    def boundingRect(self) -> QRectF:
        view_x = self._cell_x * CELL_PX_SIZE
        view_y = self._cell_y * CELL_PX_SIZE
        view_width = CELL_PX_SIZE
        view_height = CELL_PX_SIZE
        return QRectF(view_x, view_y, view_width, view_height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        rect = self.boundingRect()
        painter.fillRect(rect, self._color)

    def mousePressEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        x = int(math.floor(scene_pos.x() / CELL_PX_SIZE))
        y = int(math.floor(scene_pos.y() / CELL_PX_SIZE))


class QuickFortBlueprint(QGraphicsItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self, name: str, cell_width: int, cell_height: int):
        super().__init__()
        self._grid_pen = QPen(QBrush(Qt.black), CELL_BORDER_PX_SIZE)
        self._grid_pen.setWidth(1)
        self._grid_pen.setCosmetic(True)
        self._alpha = 255
        self._name = name
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._cells: List[List[Optional[DesignationCell]]] = [
            [None for _ in range(0, cell_height)]
            for _ in range(0, cell_width)
        ]

    def type(self) -> int:
        return QuickFortBlueprint.QT_TYPE

    def boundingRect(self) -> QRectF:
        px_width = self._cell_width * CELL_PX_SIZE
        px_height = self._cell_height * CELL_PX_SIZE
        return QRectF(0, 0, px_width, px_height)

    def _walk_cells(self, skip_empty: bool = True) -> Generator[Tuple[int, int, DesignationCell], None, None]:
        for x in range(0, self._cell_width):
            for y in range(0, self._cell_height):
                cell: Optional[DesignationCell] = self._cells[x][y]
                if skip_empty and cell is None:
                    continue
                yield x, y, cell

    def _paint_grid(self, painter: QPainter):
        painter.save()
        pix_x = self._cell_width * CELL_PX_SIZE
        pix_y = self._cell_height * CELL_PX_SIZE
        painter.setPen(self._grid_pen)
        painter.drawRect(QRectF(0, 0, pix_x, pix_y))
        for x in range(CELL_PX_SIZE, pix_x, CELL_PX_SIZE):
            painter.drawLine(x, 0, x, pix_y)
        for y in range(CELL_PX_SIZE, pix_y, CELL_PX_SIZE):
            painter.drawLine(0, y, pix_x, y)
        painter.restore()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        painter.save()
        for x, y, cell in self._walk_cells(skip_empty=True):
            cell.alpha = self._alpha
            cell.paint(painter, option, widget)
        painter.restore()
        self._paint_grid(painter)

    def mousePressEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        x = int(math.floor(scene_pos.x() / CELL_PX_SIZE))
        y = int(math.floor(scene_pos.y() / CELL_PX_SIZE))
        cell: Optional[DesignationCell] = self._cells[x][y]
        if cell is None:
            print(f'Setting cell {(x,y)}')
            self._cells[x][y] = DesignationCell(x, y)
        else:
            print(f'(Phase: {self._name}): Unsetting cell {(x,y)}')
            self._cells[x][y] = None
        self.update()


class QuickFortBlueprintViewer(QGraphicsView):

    def __init__(self):
        super().__init__()

        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(0, 0, 600, 600)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.world_matrix = QuickFortBlueprint("test", 144, 144)
        scene.addItem(self.world_matrix)
        self.fitInView(self.world_matrix, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scale = math.pow(2.0, -delta / 240.0)
        self.scale_view(scale)

    def scale_view(self, scale_factor):
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scale_factor, scale_factor)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.viewer = QuickFortBlueprintViewer()
        self.setCentralWidget(self.viewer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
    mainWin.show()
    sys.exit(app.exec_())
