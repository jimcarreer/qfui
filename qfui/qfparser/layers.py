from typing import List

import numpy

from qfui.models.layers import GridLayer
from qfui.qfparser.cells import CellParser, UnprocessedCellParser


class GridLayerParser:

    def __init__(self, cell_parser: CellParser = None):
        self._cell_parser = cell_parser or UnprocessedCellParser()

    def parse(self, relative_z: int, raw_lines: List[List[str]]):
        shape = [1, 1]
        buffer = []
        for layer_y, raw_line in enumerate(raw_lines):
            for layer_x, raw_cell in enumerate(raw_line):
                parsed = self._cell_parser.parse(layer_x, layer_y, raw_cell)
                for x, y, cell in parsed:
                    shape = [max(x + 1, shape[0]), max(y + 1, shape[1])]
                    buffer.append((x, y, cell))
        cells = numpy.ndarray(shape, dtype=object)
        for x, y, cell in buffer:
            cells[x, y] = cell
        return GridLayer(relative_z=relative_z, cells=cells)
