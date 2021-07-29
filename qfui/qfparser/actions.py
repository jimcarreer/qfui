from qfui.models.enums import Markers, SectionModes


def as_int(subject: str, col: int, tokens: list):
    return [int(tkn) for tkn in tokens]


def as_maker(subject: str, col: int, tokens: list):
    return [Markers.from_value(tkn) for tkn in tokens]


def as_mode(subject: str, col: int, tokens: list):
    return [SectionModes.from_value(tkn) for tkn in tokens]


def start(subject: str, col: int, tokens: list):
    marker = tokens.pop(0)
    comment = tokens.pop()
    ret = {"start_comment": comment} if comment else {}
    # Lau supports 1 based indexing and is what QF expects for start x, y
    ret.update({"start_x": tokens.pop(0) - 1, "start_y": tokens.pop(0) - 1} if len(tokens) == 2 else {})
    return [marker, ret]


def hidden(subject: str, col: int, tokens: list):
    marker = tokens.pop(0)
    return [marker, {"hidden": True}]


def label_or_message(subject: str, col: int, tokens: list):
    marker = tokens.pop(0)
    return [marker, {marker.value: tokens.pop(0)}]


def raw_cell(subject: str, col: int, tokens: list):
    ret = {"code_text": tokens.pop(0)}
    ret.update({"width": tokens.pop(0), "height": tokens.pop(0)} if len(tokens) == 2 else {})
    return [ret]
