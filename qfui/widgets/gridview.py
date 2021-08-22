# WIP
import math

from typing import Optional, Generator, Tuple, List

from PySide6.QtCore import QRectF, Slot, QRect, QLineF, QPoint
from PySide6.QtGui import QPainter, QMouseEvent, QPen, Qt, QBrush
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsView, QGraphicsScene, QStyleOptionGraphicsItem, QWidget, QGraphicsSceneMouseEvent,
)

from qfui.controller.messages import ControllerInterface
from qfui.models.enums import Designations
from qfui import sprites

CELL_PX_SIZE = 16
CELL_BORDER_PX_SIZE = 1


class DesignationCell(QGraphicsItem):
    QT_TYPE = QGraphicsItem.UserType + 1

    def __init__(self, cell_x: int, cell_y: int, designation: Designations):
        super().__init__()
        self._designation = designation
        self._cell_x = cell_x
        self._cell_y = cell_y
        self._cell_sprint = sprites.lookup_designation(designation)

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
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(rect, self._cell_sprint.color)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Overlay)
        painter.drawImage(QPoint(rect.x(), rect.y()), self._cell_sprint.img)


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
        painter.save()
        painter.setPen(self._grid_pen)
        painter.drawRect(self.boundingRect())
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
            self._cells[x][y] = DesignationCell(x, y, Designations.MINE)
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

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        pos = event.scenePos()
        x = int(math.floor(pos.x() / CELL_PX_SIZE))
        y = int(math.floor(pos.y() / CELL_PX_SIZE))
        print(f"Mouse click: {x}, {y}")

    def drawForeground(self, painter: QPainter, rect: QRect) -> None:
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
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scale = math.pow(2.0, -delta / 240.0)
        self.scale_view(scale)

    def scale_view(self, scale_factor):
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1.0, 1.0)).width()

        if factor < 0.25 or factor > 25:
            return

        self.scale(scale_factor, scale_factor)

    @Slot(ControllerInterface)
    def project_changed(self, _):
        self.scene().clear()
        scene = GridScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(scene)
        self.scale_view(1.0)

    @Slot(ControllerInterface, list, list)
    def layer_visibility_changed(self, controller: ControllerInterface, *_):
        self.scene().clear()
        visible = controller.visible_layers
        if not visible:
            return

        layer_items = []
        left, right, bottom, top = math.inf, -math.inf, -math.inf, math.inf
        for idx, layer in visible.items():
            layer_item = LayerItem(layer.width, layer.height)
            # TODO: CLean this up / init from Layer
            for (x, y), cell in layer.walk(lambda i, j, c: c is not None):
                layer_item._cells[x][y] = DesignationCell(x, y, cell.designation)
            start = controller.layer_start_position(idx)
            real_x = start.x * CELL_PX_SIZE
            real_y = start.y * CELL_PX_SIZE
            real_l = layer_item.boundingRect().left() - real_x
            real_r = layer_item.boundingRect().right() - real_x
            real_t = layer_item.boundingRect().top() - real_y
            real_b = layer_item.boundingRect().bottom() - real_y
            left = min(left, real_l)
            right = max(right, real_r)
            top = min(top, real_t)
            bottom = max(bottom, real_b)
            layer_item.setPos(-real_x, -real_y)
            layer_items.append(layer_item)

        bounding_w = right - left
        bounding_h = bottom - top
        print(f'{top/CELL_PX_SIZE}, {left/CELL_PX_SIZE}, {right/CELL_PX_SIZE}, {bottom/CELL_PX_SIZE}')
        print(f'{bounding_w/CELL_PX_SIZE}, {bounding_h/CELL_PX_SIZE}')
        grid_item = GridLayerItem(bounding_w/CELL_PX_SIZE, bounding_h/CELL_PX_SIZE)
        grid_item.setPos(left, top)
        for layer_item in layer_items:
            self.scene().addItem(layer_item)
        self.scene().addItem(grid_item)
        self.fitInView(grid_item, Qt.KeepAspectRatio)
