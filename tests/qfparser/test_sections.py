from collections import deque
from qfui.models.enums import SectionModes

import pytest

from qfui.models.sections import SectionStart
from qfui.qfparser.sections import SectionParser


NON_GRID_MODES = [
    SectionModes.ALIASES,
    SectionModes.META,
    SectionModes.NOTES,
    SectionModes.IGNORE,
]


@pytest.mark.parametrize("rot", [0, 1, 2, 3])
@pytest.mark.parametrize("mode, ex_md", [(f"#{m.value}", m) for m in SectionModes])
@pytest.mark.parametrize("start, ex_ss", [
    ("start  (11, 23; start comments)", SectionStart(10, 22, " start comments")),
    ("   start(19;19;mid-stairs)   ", SectionStart(18, 18, "mid-stairs")),
    ("start(1,2)", SectionStart(0, 1, None)),
    ("start( 1  2 )", SectionStart(0, 1, None)),
    ("start(33 23 space comments)", SectionStart(32, 22, "space comments")),
    ("", None)
])
@pytest.mark.parametrize("comment, ex_cm", [
    ("", None),
    ("some test comments ()  ", "some test comments ()  ")
])
@pytest.mark.parametrize("message, ex_ms", [
    ("", None),
    ("  message( some test messaging (with nested parans) )", " some test messaging (with nested parans) ")
])
@pytest.mark.parametrize("hidden, ex_hi", [
    ("", False),
    ("hidden   ( some junk we ignore (with parans) )", True),
    (" hidden()  ", True),
    ("hidden (   )", True),
])
@pytest.mark.parametrize("label, ex_lb", [
    ("", "default-test-label"),
    ("label   (my super special label() )", "my super special label() "),
    (" label(pretty standard)  ", "pretty standard"),
])
def test_section_mode_line_parsing(
        rot, mode, ex_md,
        start, ex_ss,
        comment, ex_cm,
        message, ex_ms,
        hidden, ex_hi,
        label, ex_lb
):
    # These 3 can be in any order so we rotate their order 0 - 3 times to test all combinations
    raw = deque([start, message, hidden, label])
    raw.rotate(rot)
    # This is defaulted for grid mode sections
    if ex_md not in NON_GRID_MODES and ex_ss is None:
        ex_ss = SectionStart(0, 0, None)
    raw = " ".join([r for r in raw if r])
    raw = f"{raw.rstrip()}" if raw else ""
    raw = f"{mode} {raw}{comment}"
    parser = SectionParser.try_get_parser(raw, "default-test-label")
    sec = parser.parse(raw=[])
    assert sec, f"failed completely to parse '{raw}'"
    assert sec.mode == ex_md, f"failed to get mode for '{raw}'"
    assert sec.start == ex_ss, f"failed start marker for :'{raw}'"
    assert sec.message == ex_ms, f"failed message marker for '{raw}'"
    assert sec.comment == ex_cm, f"failed comment for '{raw}'"
    assert sec.hidden == ex_hi, f"failed hidden for '{raw}'"
    assert sec.label == ex_lb, f"failed label for '{raw}'"
