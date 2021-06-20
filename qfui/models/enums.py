from __future__ import annotations

import enum
from typing import Optional, List, Dict

__SECTION_LOOKUP__ = {}
__MARKER_LOOKUP__ = {}
__DESIGNATION_LOOKUP__ = {}


class Designations(enum.Enum):

    MINE                = "d"
    CHOP_TREE           = "t"
    CHANNEL             = "h"
    UP_STAIR            = "u"
    DOWN_STAIR          = "j"
    UP_DOWN_STAIR       = "i"
    RAMP                = "r"
    REMOVE_RAMPS        = "z"
    GATHER              = "p"
    SMOOTH              = "s"
    ENGRAVE             = "e"
    FORTIFICATION       = "F"
    TRACK               = "T"
    TOGGLE_ENGRAVINGS   = "v"
    TOGGLE_MARKER       = "M"
    REMOVE_CONSTRUCTION = "n"
    REMOVE_DESIGNATION  = "x"
    CLAIM               = "bc"
    FORBID              = "bf"
    MELT                = "bm"
    REMOVE_MELT         = "bM"
    DUMP                = "bd"
    REMOVE_DUMP         = "bD"
    HIDE                = "bh"
    REMOVE_HIDE         = "bH"
    HIGH_TRAFFIC        = "oh"
    NORMAL_TRAFFIC      = "on"
    LOW_TRAFFIC         = "ol"
    RESTRICTED_TRAFFIC  = "or"

    @staticmethod
    def _lookup() -> Dict[str, Markers]:
        global __DESIGNATION_LOOKUP__
        if not __DESIGNATION_LOOKUP__:
            __DESIGNATION_LOOKUP__ = {m.value: m for m in Designations}
        return __DESIGNATION_LOOKUP__

    @staticmethod
    def from_value(marker: str) -> Optional[Markers]:
        return Designations._lookup().get(marker, None)

    @staticmethod
    def values() -> List[str]:
        return sorted(Designations._lookup().keys())

    def __str__(self):
        return self.value


class Markers(enum.Enum):

    LABEL   = "label"
    START   = "start"
    MESSAGE = "message"
    HIDDEN  = "hidden"

    @staticmethod
    def _lookup() -> Dict[str, Markers]:
        global __MARKER_LOOKUP__
        if not __MARKER_LOOKUP__:
            __MARKER_LOOKUP__ = {m.value: m for m in Markers}
        return __MARKER_LOOKUP__

    @staticmethod
    def from_value(marker: str) -> Optional[Markers]:
        return Markers._lookup().get(marker, None)

    @staticmethod
    def values() -> List[str]:
        return sorted(Markers._lookup().keys())

    def __str__(self):
        return self.value


class SectionModes(enum.Enum):

    DIG     = "dig"
    BUILD   = "build"
    PLACE   = "place"
    ZONE    = "zone"
    QUERY   = "query"
    META    = "meta"
    NOTES   = "notes"
    IGNORE  = "ignore"
    ALIASES = "aliases"

    @staticmethod
    def _lookup():
        global __SECTION_LOOKUP__
        if not __SECTION_LOOKUP__:
            __SECTION_LOOKUP__ = {m.value: m for m in SectionModes}
        return __SECTION_LOOKUP__

    @staticmethod
    def from_value(mode: str) -> Optional[SectionModes]:
        return SectionModes._lookup().get(mode, None)

    @staticmethod
    def values() -> List[str]:
        return sorted(SectionModes._lookup().keys())

    def __str__(self):
        return self.value
