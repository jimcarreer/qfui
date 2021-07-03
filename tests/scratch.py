from __future__ import annotations

import json
import csv
from qfui.models.enums import SectionModes
from qfui.qfparser.importers import CSVImporter
from qfui.models.serialize import SerializingJSONEncoder

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


loader = CSVImporter()
sections = loader.load('data/dreamfort.csv')
# print(json.dumps([s for s in thing._sections if s.mode is SectionModes.ZONE], cls=SerializingJSONEncoder, indent=2))
with open('data/dreamfort.json', 'w') as fh:
    json.dump(sections, fh, indent=2, cls=SerializingJSONEncoder)

