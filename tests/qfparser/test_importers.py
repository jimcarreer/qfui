import json
import uuid
from unittest.mock import patch

from qfui.models.serialize import SerializingJSONEncoder
from qfui.qfparser.importers import CSVImporter

TEST_UUIDS_COUNT = 0


def mock_uuid():
    global TEST_UUIDS_COUNT
    TEST_UUIDS_COUNT += 1
    return uuid.UUID(int=TEST_UUIDS_COUNT)


@patch('uuid.uuid4', mock_uuid)
def test_dreamfort_parsing():
    importer = CSVImporter()
    sections = importer.load("data/dreamfort.csv")
    actual_sections = json.dumps(sections, indent=2, cls=SerializingJSONEncoder)
    with open("data/dreamfort.json", "r") as fh:
        assert actual_sections == fh.read()
