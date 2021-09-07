import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from qfui.models.enums import SectionModes
from qfui.models.sections import GridSection, Section
from qfui.qfparser.sections import SectionParser


class Importer(ABC):

    @abstractmethod
    def load(self, filepath: Union[str, Path]) -> List[Section]:
        pass


class CSVImporter(Importer):

    def load(self,  filepath: Union[str, Path]):
        with open(filepath, "r") as fh:
            reader = csv.reader(fh, dialect="excel")
            return self._load(reader)

    @staticmethod
    def _load(reader) -> List[Section]:
        section_line_no = None
        current_parser = None
        raw_section_data = []
        parsed_sections = []
        for line_no, row in enumerate(reader):
            new_parser = SectionParser.try_get_parser(row[0], f"{len(parsed_sections) + 1}") if row else None
            section_line_no = line_no if new_parser else section_line_no
            if new_parser is None:
                raw_section_data.append(row)
            if line_no == 0 and new_parser is None:
                section = GridSection(mode=SectionModes.DIG, label=f"{len(parsed_sections) + 1}")
                new_parser = SectionParser.parser_for(section)
                section_line_no = line_no
            if current_parser is None:
                current_parser = new_parser
            if new_parser and new_parser != current_parser:
                section = current_parser.parse(raw_section_data)
                parsed_sections.append(section)
                raw_section_data = []
                current_parser = new_parser
        if raw_section_data and current_parser:
            parsed_sections.append(current_parser.parse(raw_section_data))
        return parsed_sections
