from dataclasses import dataclass, field
from typing import List

from qfui.models.sections import Section


@dataclass
class Project:

    sections: List[Section] = field(default_factory=list)

