import csv
from typing import List

from qfui.models.enums import SectionModes
from qfui.models.sections import GridSection, Section
from qfui.qfparser.sections import SectionParser


class Blueprint:

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._sections: List[Section] = []

    @property
    def filepath(self):
        return self._filepath

    @property
    def sections(self):
        return self._sections

    def load(self):
        with open(self._filepath, "r") as fh:
            reader = csv.reader(fh, dialect="excel")
            self._load(reader)

    def _load(self, reader):
        section_line_no = None
        current_parser = None
        raw_section_data = []
        for line_no, row in enumerate(reader):
            new_parser = SectionParser.try_get_parser(row[0], f"{len(self._sections) + 1}") if row else None
            section_line_no = line_no if new_parser else section_line_no
            if new_parser is None:
                raw_section_data.append(row)
            if line_no == 0 and new_parser is None:
                section = GridSection(SectionModes.DIG, f"{len(self._sections) + 1}")
                new_parser = SectionParser.parser_for(section)
                section_line_no = line_no
            if current_parser is None:
                current_parser = new_parser
            if new_parser and new_parser != current_parser:
                section = current_parser.parse(raw_section_data)
                self._sections.append(section)
                raw_section_data = []
                current_parser = new_parser
        if raw_section_data and current_parser:
            self._sections.append(current_parser.parse(raw_section_data))
