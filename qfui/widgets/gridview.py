# WIP
import math

from typing import Optional, Generator, Tuple, List

from PySide6.QtCore import QRectF, Slot, QRect, QPointF, QLine, QLineF
from PySide6.QtGui import QPainter, QMouseEvent, QPen, Qt, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsView, QGraphicsScene, QStyleOptionGraphicsItem, QWidget,
)

from qfui.controller.messages import ControllerInterface
from qfui.models.layers import GridLayer
from qfui.models.project import SectionLayerIndex

CELL_PX_SIZE = 20
CELL_BORDER_PX_SIZE = 1


class DesignationCell(QGraphicsItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self, cell_x: int, cell_y: int):
        super().__init__()
        self._cell_x = cell_x
        self._cell_y = cell_y
        self._color = QColor(255, 0, 0, 255)

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


class GridLayerItem(QGraphicsItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self, cell_width: int, cell_height: int):
        super().__init__()
        self._grid_pen = QPen(QBrush(Qt.black), CELL_BORDER_PX_SIZE)
        self._grid_pen.setStyle(Qt.SolidLine)
        self._grid_pen.setWidth(1)
        self._grid_pen.setCosmetic(True)
        self._cell_width = cell_width
        self._cell_height = cell_height

    @property
    def cell_width(self) -> int:
        return self._cell_width

    @property
    def cell_height(self) -> int:
        return self._cell_height

    def type(self) -> int:
        return GridLayerItem.QT_TYPE

    def boundingRect(self) -> QRectF:
        px_width = self._cell_width * CELL_PX_SIZE
        px_height = self._cell_height * CELL_PX_SIZE
        return QRectF(0, 0, px_width, px_height)

    def _paint_grid(self, painter: QPainter):
        pix_x = self._cell_width * CELL_PX_SIZE
        pix_y = self._cell_height * CELL_PX_SIZE
        painter.save()
        painter.setPen(self._grid_pen)
        #painter.drawRect(QRectF(0, 0, pix_x, pix_y))
        for x in range(0, pix_x + CELL_PX_SIZE, CELL_PX_SIZE):
            painter.drawLine(x, 0, x, pix_y)
        for y in range(0, pix_y + CELL_PX_SIZE, CELL_PX_SIZE):
            painter.drawLine(0, y, pix_x, y)
        painter.restore()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        painter.save()
        self._paint_grid(painter)
        painter.restore()


class LayerItem(GridLayerItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self,  cell_width: int, cell_height: int, is_active: bool = False):
        super().__init__(cell_width, cell_height)
        self._is_active = is_active
        self._grid_pen.setStyle(Qt.SolidLine)
        self._cells: List[List[Optional[DesignationCell]]] = [
            [None for _ in range(0, cell_height)]
            for _ in range(0, cell_width)
        ]

    def type(self) -> int:
        return LayerItem.QT_TYPE

    def _walk_cells(self, skip_empty: bool = True) -> Generator[Tuple[int, int, DesignationCell], None, None]:
        for x in range(0, self._cell_width):
            for y in range(0, self._cell_height):
                cell: Optional[DesignationCell] = self._cells[x][y]
                if skip_empty and cell is None:
                    continue
                yield x, y, cell

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        painter.save()
        for x, y, cell in self._walk_cells(skip_empty=True):
            cell.paint(painter, option, widget)
        # Only the active layer has it's grid painted
        if self._is_active:
            self._paint_grid(painter)
        painter.restore()

    def mousePressEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
        x = int(math.floor((scene_pos.x() - self.x()) / CELL_PX_SIZE))
        y = int(math.floor((scene_pos.y() - self.y()) / CELL_PX_SIZE))
        print(f'Clicked cell {(x, y)}')
        cell: Optional[DesignationCell] = self._cells[x][y]
        if cell is None:
            print(f'Setting cell {(x,y)}')
            self._cells[x][y] = DesignationCell(x, y)
        else:
            print(f'(Unsetting cell {(x,y)}')
            self._cells[x][y] = None
        self.update()


class GridScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)
        self._grid_pen = QPen(QBrush(Qt.black), CELL_BORDER_PX_SIZE)
        self._grid_pen.setStyle(Qt.DotLine)
        self._grid_pen.setWidth(1)
        self._grid_pen.setCosmetic(True)

    def drawBackground(self, painter: QPainter, rect: QRect) -> None:
        painter.save()
        painter.setPen(self._grid_pen)
        left = int(rect.left()) - (int(rect.left()) % CELL_PX_SIZE)
        right = int(rect.right()) - (int(rect.right()) % CELL_PX_SIZE)
        top = int(rect.top()) - (int(rect.top()) % CELL_PX_SIZE)
        bottom = int(rect.bottom()) - (int(rect.bottom()) % CELL_PX_SIZE)
        lines = []
        for x in range(left, right + CELL_PX_SIZE, CELL_PX_SIZE):
            lines.append(QLineF(x, top, x, bottom + CELL_PX_SIZE))
        for y in range(top, bottom + CELL_PX_SIZE, CELL_PX_SIZE):
            lines.append(QLineF(left, y, right + CELL_PX_SIZE, y))
        painter.drawLines(lines)
        painter.restore()


class LayerViewer(QGraphicsView):

    def __init__(self):
        super().__init__()

        scene = GridScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scale = math.pow(2.0, -delta / 240.0)
        self.scale_view(scale)

    def scale_view(self, scale_factor):
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scale_factor, scale_factor)

    @Slot(ControllerInterface)
    def project_changed(self, _):
        self.scene().clear()

    @Slot(ControllerInterface, list)
    def layer_visibility_changed(self, controller: ControllerInterface, visible: List[SectionLayerIndex]):
        self.scene().clear()
        if not visible:
            return

        layer_items = []
        max_w, max_h = 1, 1
        for idx in visible:
            layer = controller.grid_layer(idx)
            max_w, max_h = max(layer.width, max_w), max(layer.height, max_h)

            layer_item = LayerItem(layer.width, layer.height)
            for (x, y), cell in layer.walk(lambda i, j, c: c is not None):
                layer_item._cells[x][y] = DesignationCell(x, y)
            layer_items.append(layer_item)

        grid_item = GridLayerItem(max_w, max_h)
        for layer_item in layer_items:
            #layer_item.setPos(self._grid_origin[0] - CELL_PX_SIZE/2 - 1, self._grid_origin[1] - CELL_PX_SIZE/2)
            #new_x = max(0, center_gx - int((layer_item.cell_width)/2))
            #new_y = max(0, center_gy - int((layer_item.cell_height)/2))
            #print(f'{layer_item} {new_x} {new_y}')
            #layer_item.setPos(new_x * CELL_PX_SIZE, new_y * CELL_PX_SIZE)
            self.scene().addItem(layer_item)

        self.scene().addItem(grid_item)
        self.fitInView(grid_item, Qt.KeepAspectRatio)
