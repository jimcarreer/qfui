from typing import List

from qfui.models.sections import Section


class ProjectController:

    def __init__(self, sections: List[Section] = None):
        self._sections: List[Section] = sections or []

    @property
    def sections(self) -> List[Section]:
        return self._sections
