from dataclasses import dataclass

from PySide6.QtGui import QImage, QColor

from qfui.models.enums import Designations

__LOOKUP__ = {}
__SPRITE_SIZE__ = 16
__SHEET_WIDTH__ = 256
__SHEET_HEIGHT__ = 256


__DESIGNATION_SPRITES__ = {
    Designations.MINE: (12, 1),
    Designations.UP_DOWN_STAIR: (8, 5),
    Designations.UP_STAIR: (12, 3),
    Designations.DOWN_STAIR: (14, 3),
}

__DESIGNATION_COLORS__ = {
    Designations.MINE: QColor(139, 69, 19),
    Designations.UP_DOWN_STAIR: QColor(139, 69, 19),
    Designations.UP_STAIR: QColor(139, 69, 19),
    Designations.DOWN_STAIR: QColor(139, 69, 19),
}

__FALLBACK_SPRITE__ = (0, 0)
__FALLBACK_COLOR__ = QColor(223, 0, 254)


@dataclass
class CellSprite:

    img: QImage
    color: QColor


def initialize(sheet: QImage):
    global __LOOKUP__, __SPRITE_SIZE__, __SHEET_HEIGHT__, __SHEET_WIDTH__

    if __LOOKUP__:
        return

    if sheet.width() != __SHEET_WIDTH__ or sheet.height() != __SHEET_HEIGHT__:
        raise RuntimeError("Invalid sheet dimensions")  # TODO: Better exception

    for y in range(0, __SHEET_WIDTH__, __SPRITE_SIZE__):
        for x in range(0, __SHEET_HEIGHT__, __SPRITE_SIZE__):
            loc = int(x / __SPRITE_SIZE__), int(y / __SPRITE_SIZE__)
            __LOOKUP__[loc] = sheet.copy(x, y, __SPRITE_SIZE__, __SPRITE_SIZE__)


def lookup_designation(designation: Designations) -> CellSprite:
    global __LOOKUP__, __FALLBACK_SPRITE__, __FALLBACK_COLOR__, __DESIGNATION_SPRITES__, __DESIGNATION_COLORS__
    color = __DESIGNATION_COLORS__.get(designation, __FALLBACK_COLOR__)
    sprite = __DESIGNATION_SPRITES__.get(designation, __FALLBACK_SPRITE__)
    return CellSprite(sprite, color)
