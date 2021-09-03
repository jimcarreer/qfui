import re
from abc import ABC, abstractmethod
from typing import List, Optional, Generator, Tuple

import numpy
from pyparsing import (
    printables, nums,
    Literal, Optional as ParserOptional, ParseException, Suppress, White, Word, ZeroOrMore
)

from qfui.models.cells import Cell, DesignationCell, UnprocessedCell
from qfui.models.enums import Designations
from qfui.qfparser import actions


__EMPTY_CELL_REGEX__ = re.compile(r"^[~`\s]*$")


class ExpandingCellParser:

    EXPAND_OPEN   = Suppress("(")
    EXPAND_CLOSE  = Suppress(")")
    NULL_SPACE    = Suppress(ZeroOrMore(White()))
    DIMENSION     = Word(nums).setParseAction(actions.as_int)
    CODE_TEXT_EXP = Word(printables, excludeChars="()")
    DIMENSIONS    = NULL_SPACE + DIMENSION + Suppress(Literal('x')) + NULL_SPACE + DIMENSION + NULL_SPACE
    DIMENSIONS    = EXPAND_OPEN + DIMENSIONS + EXPAND_CLOSE
    CELL_PARSER   = NULL_SPACE + CODE_TEXT_EXP + NULL_SPACE + ParserOptional(DIMENSIONS) + NULL_SPACE
    CELL_PARSER   = CELL_PARSER.setParseAction(actions.raw_cell)

    def _try_parse_expand_raw(self, raw_cell_text: str) -> Optional[dict]:
        try:
            return self.CELL_PARSER.parseString(raw_cell_text, parseAll=True)[0]
        except ParseException:
            return None

    @staticmethod
    def _expand_kwargs(raw: str, layer_x: int, layer_y: int, width: int, height: int) -> Generator[tuple, None, None]:
        expanded = False
        for x_offset in range(0, width):
            for y_offset in range(0, height):
                yield layer_x + x_offset, layer_y + y_offset, {
                    "from_expansion": expanded,
                    "raw_text": raw if not expanded else None
                }
                expanded = True


class CellParser(ABC):

    @abstractmethod
    def parse(self, layer_x: int, layer_y: int, raw_cell: str) -> List[Cell]:
        pass


class DesignationCellParser(CellParser, ExpandingCellParser):

    __CODE_TEXT_REGEX__ = re.compile(r"^(?P<designation>[a-zA-Z]{1,2})?(?P<priority>[1-7])?$")

    @staticmethod
    def _skip_cell(raw_cell: str) -> bool:
        return __EMPTY_CELL_REGEX__.match(raw_cell) is not None

    def parse(self, layer_x: int, layer_y: int, raw_cell: str) -> List[Tuple[int, int, Cell]]:
        cells = []
        if self._skip_cell(raw_cell):
            return cells

        if not (parsed := self._try_parse_expand_raw(raw_cell)):
            # TODO: Log parsing error
            return cells
        code_text = parsed["code_text"]
        if not (matches := self.__CODE_TEXT_REGEX__.match(code_text)):
            # TODO: Log parsing error
            return cells

        designation = matches.group("designation")
        if designation and designation not in Designations.values():
            # TODO: Log parsing error
            return cells

        width = parsed.get("width", 1)
        height = parsed.get("height", 1)
        priority = int(matches.group("priority") or 4)
        designation = Designations.from_value(designation) or Designations.MINE
        for x, y, cell_kwargs in self._expand_kwargs(raw_cell, layer_x, layer_y, width, height):
            cell_kwargs["priority"] = int(priority)
            cell_kwargs["designation"] = designation
            cells.append((x, y, DesignationCell(**cell_kwargs)))
        return cells


class UnprocessedCellParser(CellParser, ExpandingCellParser):

    @staticmethod
    def _skip_cell(raw_cell: str) -> bool:
        return __EMPTY_CELL_REGEX__.match(raw_cell) is not None

    def parse(self, layer_x: int, layer_y: int, raw_cell: str) -> List[Tuple[int, int, Cell]]:
        cells = []
        if self._skip_cell(raw_cell):
            return cells

        if not (parsed := self._try_parse_expand_raw(raw_cell)):
            # TODO: Log parsing error
            return cells

        width = parsed.get("width", 1)
        height = parsed.get("height", 1)
        code_text = parsed["code_text"]
        for x, y, cell_kwargs in self._expand_kwargs(raw_cell, layer_x, layer_y, width, height):
            cell_kwargs["code_text"] = code_text
            cells.append((x, y, UnprocessedCell(**cell_kwargs)))
        return cells
