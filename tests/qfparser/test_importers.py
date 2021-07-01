import json

from qfui.models.serialize import SerializingJSONEncoder
from qfui.qfparser.importers import CSVImporter


def test_dreamfort_parsing():
    importer = CSVImporter()
    sections = importer.load("data/dreamfort.csv")
    actual_sections = json.dumps(sections, indent=2, cls=SerializingJSONEncoder)
    with open("data/dreamfort.json", "r") as fh:
        assert actual_sections == fh.read()
