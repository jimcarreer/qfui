from __future__ import annotations

import json
import csv
import uuid
from unittest.mock import patch

from qfui.models.enums import SectionModes
from qfui.qfparser.importers import CSVImporter
from qfui.models.serialize import SerializingJSONEncoder


class SequentialUUID:

    def __init__(self):
        self._counter = 0

    def __call__(self):
        self._counter += 1
        return uuid.UUID(int=self._counter)


with open('data/dreamfort.csv', 'r') as csvfh:
    prefixes = [f'#{v}' for v in SectionModes.values()]
    reader = csv.reader(csvfh)
    sections = []
    for idx, row in enumerate(reader):
        if not row:
            continue
        first = row[0]
        if any(first.startswith(v) for v in prefixes):
            sections.append(first)

    print(json.dumps(sections, indent=2))


@patch('uuid.uuid4', SequentialUUID())
def make_dump_dream():
    loader = CSVImporter()
    sections = loader.load('data/dreamfort.csv')
    # print(json.dumps([s for s in thing._sections if s.mode is SectionModes.ZONE], cls=SerializingJSONEncoder, indent=2))
    with open('data/dreamfort.json', 'w') as fh:
        json.dump(sections, fh, indent=2, cls=SerializingJSONEncoder)


@patch('uuid.uuid4', SequentialUUID())
def make_dump_clover():
    loader = CSVImporter()
    sections = loader.load('data/cloverdorms.csv')
    with open('data/cloverdorms.json', 'w') as fh:
        json.dump(sections, fh, indent=2, cls=SerializingJSONEncoder)


make_dump_dream()
make_dump_clover()
