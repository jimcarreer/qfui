from __future__ import annotations

from abc import ABC, abstractmethod
from functools import reduce
from typing import List, Optional, Union

from pyparsing import (
    alphas, printables, nums,
    Combine, Forward, Group, Literal, OneOrMore, Optional as ParserOptional, ParseException, Suppress, White, Word,
    ZeroOrMore
)

from qfui.models.enums import Markers, SectionModes
from qfui.models.layers import RawLayer
from qfui.models.sections import RawSection, GridSection, SectionStart
from qfui.qfparser import actions
from qfui.qfparser.cells import DesignationCellParser, CellParser, UnprocessedCellParser
from qfui.qfparser.layers import GridLayerParser


class SectionParser(ABC):

    # Text Handling Helpers
    NULL_SPACE    = ZeroOrMore(White())
    SKIP_WHITE    = Suppress(NULL_SPACE)
    NP_TEXT       = NULL_SPACE + Word(printables, excludeChars="()") + NULL_SPACE
    BP_TEXT       = Forward()
    BP_TEXT      << Combine(Group("(" + ZeroOrMore(BP_TEXT | NP_TEXT | White()) + ")"))
    COM_BLOCK     = Combine(ZeroOrMore(BP_TEXT | NP_TEXT) + NULL_SPACE).leaveWhitespace()
    # Marker Primitives
    MARK_OPEN     = Suppress("(")
    MARK_CLOSE    = Suppress(")")
    LABEL_TEXT    = Combine(Word(alphas) + Word(printables))
    XY_COORD      = Word(nums).setParseAction(actions.as_int)
    XY_SEP        = (Suppress(",") | Suppress(";") | Suppress(OneOrMore(White())))
    XY_CORDS      = XY_COORD + XY_SEP + XY_COORD + ParserOptional(XY_SEP)

    # Start marker
    MARK_START    = Literal(str(Markers.START)).setParseAction(actions.as_maker)
    START_COM     = Combine(NULL_SPACE + ParserOptional(COM_BLOCK))
    MARK_START    = MARK_START + SKIP_WHITE + MARK_OPEN + ParserOptional(XY_CORDS) + START_COM + MARK_CLOSE
    MARK_START    = Group(MARK_START.setParseAction(actions.start))

    # Message marker
    MARK_MESSAGE  = Literal(str(Markers.MESSAGE)).setParseAction(actions.as_maker)
    MARK_MESSAGE  = MARK_MESSAGE + MARK_OPEN + COM_BLOCK + MARK_CLOSE
    MARK_MESSAGE  = Group(MARK_MESSAGE.setParseAction(actions.label_or_message))

    # Hidden marker
    MARK_HIDDEN   = Literal(str(Markers.HIDDEN)).setParseAction(actions.as_maker)
    MARK_HIDDEN   = MARK_HIDDEN + MARK_OPEN + Suppress(COM_BLOCK) + MARK_CLOSE
    MARK_HIDDEN   = Group(MARK_HIDDEN.setParseAction(actions.hidden))

    # Label marker
    MARK_LABEL    = Literal(str(Markers.LABEL)).setParseAction(actions.as_maker)
    MARK_LABEL    = MARK_LABEL + MARK_OPEN + Combine(Word(alphas) + COM_BLOCK) + MARK_CLOSE
    MARK_LABEL    = Group(MARK_LABEL.setParseAction(actions.label_or_message))

    # Main Grammar
    MARKERS       = ParserOptional(MARK_START)
    MARKERS      &= ParserOptional(MARK_MESSAGE)
    MARKERS      &= ParserOptional(MARK_HIDDEN)
    MARKERS      &= ParserOptional(MARK_LABEL)
    MODE_NAME     = Suppress("#") + (reduce(lambda a, b: a | b, map(lambda m: Literal(str(m)), SectionModes)))
    MODE_NAME     = MODE_NAME.setParseAction(actions.as_mode)
    COMMENT       = Group(ParserOptional(COM_BLOCK))
    MODE_PARSER   = MODE_NAME + SKIP_WHITE + MARKERS + COMMENT

    __MODE_TO_SECTION__ = {
        SectionModes.DIG: GridSection,
        SectionModes.BUILD: GridSection,
        SectionModes.PLACE: GridSection,
        SectionModes.QUERY: GridSection,
        SectionModes.ZONE: GridSection,
    }

    def __init__(self, section: Union[RawSection, GridSection]):
        self._section = section

    @abstractmethod
    def parse(self, raw: List[List[str]]) -> Union[RawSection, GridSection]:
        pass

    @staticmethod
    def parser_for(section: Union[GridSection, RawSection]):
        return RawSectionParser(section) if isinstance(section, RawSection) else GridSectionParser(section)

    @classmethod
    def try_get_parser(cls, raw_mode_line: str, label_default: str) -> Optional[SectionParser]:
        try:
            nodes = cls.MODE_PARSER.parseString(raw_mode_line, parseAll=True)
        except ParseException:
            return None
        kwargs = {"label": label_default, "mode": nodes.pop(0)}
        while nodes:
            node = nodes.pop()
            kwargs.update(node[1] if len(node) == 2 else {"comment": node[0]})
        if "comment" in kwargs and not kwargs["comment"]:
            kwargs.pop("comment")
        start = {
            "x": kwargs.pop("start_x", None),
            "y": kwargs.pop("start_y", None),
            "comment": kwargs.pop("start_comment", None)
        }
        kwargs['start'] = None if all(v is None for v in start.values()) else SectionStart(**start)
        sec_cls = cls.__MODE_TO_SECTION__.get(kwargs["mode"], RawSection)
        section = sec_cls(**kwargs)
        return cls.parser_for(section)


class RawSectionParser(SectionParser):

    def parse(self, raw: List[List[str]]) -> RawSection:
        section: RawSection = self._section
        section.layer = RawLayer(raw_lines=raw)
        return section


class GridSectionParser(SectionParser):

    __MODE_TO_CELL_PARSER__ = {
        SectionModes.DIG: DesignationCellParser,
        SectionModes.BUILD: UnprocessedCellParser,
        SectionModes.PLACE: UnprocessedCellParser,
        SectionModes.QUERY: UnprocessedCellParser,
        SectionModes.ZONE: UnprocessedCellParser,
    }

    def __init__(self, section: Union[RawSection, GridSection]):
        super().__init__(section)
        cell_parser = self.__MODE_TO_CELL_PARSER__.get(section.mode, CellParser)
        self._layer_parser = GridLayerParser(cell_parser=cell_parser())

    def parse(self, raw: List[List[str]]):
        section: GridSection = self._section
        layer_z = 0
        layer_raw_lines = []
        for raw_line in raw:
            if raw_line and raw_line[0] in ["#>", "#<"]:
                section.layers += [self._layer_parser.parse(layer_z, layer_raw_lines)] if layer_raw_lines else []
                layer_z += 1 if raw_line[0] == "#>" else -1
                layer_raw_lines = []
            elif not raw_line or not raw_line[0].startswith("#"):
                layer_raw_lines.append(raw_line)
        if layer_raw_lines:
            section.layers += [self._layer_parser.parse(layer_z, layer_raw_lines)]
        return section
