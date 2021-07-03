from typing import List, Optional

from qfui.models.project import Project
from qfui.models.sections import Section


class ProjectController:

    def __init__(self, project: Optional[Project] = None):
        self._project = project or Project()

    @property
    def sections(self) -> List[Section]:
        return self._project.sections
