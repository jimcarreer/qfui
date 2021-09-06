import logging
from dataclasses import dataclass

from PySide6.QtCore import QPoint
from PySide6.QtGui import QImage, QColor, QPainter, QBitmap, QPixmap, QIcon

from qfui.models.enums import Designations


__LOGGER__ = logging.getLogger(__name__)
__MASK_LOOKUP__ = {}
__SPRITE_LOOKUP__ = {}
__SPRITE_SIZE__ = 16
__SHEET_WIDTH__ = 256
__SHEET_HEIGHT__ = 256


__DESIGNATION_SPRITES__ = {
    Designations.MINE: (12, 1),
    Designations.UP_DOWN_STAIR: (8, 5),
    Designations.UP_STAIR: (12, 3),
    Designations.DOWN_STAIR: (14, 3),
    Designations.REMOVE_RAMPS: (14, 1),
}

__DESIGNATION_COLORS__ = {
    Designations.MINE: QColor(139, 69, 19),
    Designations.UP_DOWN_STAIR: QColor(139, 69, 19),
    Designations.UP_STAIR: QColor(139, 69, 19),
    Designations.DOWN_STAIR: QColor(139, 69, 19),
    Designations.REMOVE_RAMPS: QColor(139, 69, 19),
}

__FALLBACK_SPRITE__ = (0, 0)
__FALLBACK_COLOR__ = QColor(223, 0, 254)


class CellSprite:

    def __init__(self, mask: QImage, color: QColor):
        self._mask = mask
        self._color = color
        painter = QPainter()
        self._image = QImage(self._mask.size(), self._mask.format())
        self._image.fill(self._color)
        painter.begin(self._image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Overlay)
        painter.drawImage(QPoint(0, 0), self._mask)
        painter.end()
        self._pixmap = QPixmap(self._image)
        self._icon = QIcon(self._pixmap)

    @property
    def image(self) -> QImage:
        return self._image

    @property
    def pixmap(self) -> QPixmap:
        return self._pixmap

    @property
    def icon(self) -> QIcon:
        return self._icon


def initialize(sheet: QImage):
    global __MASK_LOOKUP__, __SPRITE_SIZE__, __SHEET_HEIGHT__, __SHEET_WIDTH__

    if __MASK_LOOKUP__:
        return

    if sheet.width() != __SHEET_WIDTH__ or sheet.height() != __SHEET_HEIGHT__:
        raise RuntimeError("Invalid sheet dimensions")  # TODO: Better exception

    for y in range(0, __SHEET_WIDTH__, __SPRITE_SIZE__):
        for x in range(0, __SHEET_HEIGHT__, __SPRITE_SIZE__):
            loc = int(x / __SPRITE_SIZE__), int(y / __SPRITE_SIZE__)
            __MASK_LOOKUP__[loc] = sheet.copy(x, y, __SPRITE_SIZE__, __SPRITE_SIZE__)


def lookup_designation(designation: Designations) -> CellSprite:
    global __LOGGER__, __MASK_LOOKUP__, __FALLBACK_SPRITE__, __FALLBACK_COLOR__, \
           __DESIGNATION_SPRITES__, __DESIGNATION_COLORS__, __SPRITE_LOOKUP__
    color = __DESIGNATION_COLORS__.get(designation, __FALLBACK_COLOR__)
    cache_idx = designation, color.red(), color.blue(), color.green()
    if sprite := __SPRITE_LOOKUP__.get(cache_idx):
        return sprite
    mask = __DESIGNATION_SPRITES__.get(designation, __FALLBACK_SPRITE__)
    if designation and (color == __FALLBACK_COLOR__ or mask == __FALLBACK_SPRITE__):
        __LOGGER__.debug(f'Designation {designation.name} ({designation}) used a fallback color or sprite')
    elif designation is None:
        __LOGGER__.debug(f'Got empty designation')
    sprite = CellSprite(mask=__MASK_LOOKUP__[mask], color=color)
    __SPRITE_LOOKUP__[cache_idx] = sprite
    return sprite
