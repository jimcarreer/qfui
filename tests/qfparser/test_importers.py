import json
import uuid

import pytest

from qfui.models.serialize import SerializingJSONEncoder
from qfui.qfparser.importers import CSVImporter


class SequentialUUID:

    def __init__(self):
        self._counter = 0

    def __call__(self):
        self._counter += 1
        return uuid.UUID(int=self._counter)


@pytest.mark.parametrize("filename", ("dreamfort", "cloverdorms"))
def test_qf_import(monkeypatch, filename: str):
    monkeypatch.setattr("uuid.uuid4", SequentialUUID())
    importer = CSVImporter()
    sections = importer.load(f"data/{filename}.csv")
    actual_sections = json.dumps(sections, indent=2, cls=SerializingJSONEncoder)
    with open(f"data/{filename}.json", "r") as fh:
        assert actual_sections == fh.read()
