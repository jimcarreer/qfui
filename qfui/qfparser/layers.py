from typing import List

from qfui.models.layers import GridLayer
from qfui.qfparser.cells import CellParser, UnprocessedCellParser


class GridLayerParser:

    def __init__(self, cell_parser: CellParser = None):
        self._cell_parser = cell_parser or UnprocessedCellParser()

    def parse(self, relative_z: int, raw_lines: List[List[str]]):
        cells = []
        for layer_y, raw_line in enumerate(raw_lines):
            for layer_x, raw_cell in enumerate(raw_line):
                cells += self._cell_parser.parse(layer_x, layer_y, raw_cell)
        return GridLayer(relative_z=relative_z, cells=cells)
