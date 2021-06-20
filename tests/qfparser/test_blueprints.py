import json

from qfui.models.serialize import SerializingJSONEncoder
from qfui.qfparser.blueprints import Blueprint


def test_dreamfort_parsing():
    bp = Blueprint('data/dreamfort.csv')
    bp.load()
    actual_sections = json.dumps(bp._sections, indent=2, cls=SerializingJSONEncoder)
    with open('data/dreamfort.json', 'r') as fh:
        assert actual_sections == fh.read()
