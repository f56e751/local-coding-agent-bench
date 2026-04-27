"""T3 grader — JSON parser with string escape support.

These tests are split into two groups:
  - Existing tests: pass already against the starter (and MUST stay green).
  - Regression fixes: currently fail; the agent must make them pass.
"""
import json as _stdjson
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "starter"))

from parser import parse, JSONDecodeError  # noqa: E402


# ====================================================================
# Group A — behaviors that already work; must remain passing.
# ====================================================================

class TestExistingBehaviors:
    def test_null(self):
        assert parse("null") is None

    def test_true_false(self):
        assert parse("true") is True
        assert parse("false") is False

    def test_integer(self):
        assert parse("42") == 42
        assert parse("-17") == -17
        assert parse("0") == 0

    def test_float(self):
        assert parse("3.14") == 3.14
        assert parse("-0.5") == -0.5

    def test_simple_string(self):
        assert parse('"hello"') == "hello"
        assert parse('""') == ""

    def test_array_of_ints(self):
        assert parse("[1, 2, 3]") == [1, 2, 3]

    def test_empty_array(self):
        assert parse("[]") == []

    def test_empty_object(self):
        assert parse("{}") == {}

    def test_object_with_string_value(self):
        assert parse('{"greeting": "hi"}') == {"greeting": "hi"}

    def test_nested_structures(self):
        doc = '{"a": [1, {"b": null}], "c": true}'
        assert parse(doc) == {"a": [1, {"b": None}], "c": True}

    def test_trailing_garbage_rejected(self):
        import pytest
        with pytest.raises(JSONDecodeError):
            parse('"ok" garbage')

    def test_whitespace_tolerance(self):
        assert parse("  [1  ,  2 ]  ") == [1, 2]


# ====================================================================
# Group B — the bug.  The starter parser fails these; the fix must
# make them pass WITHOUT breaking Group A above.
# ====================================================================

class TestEscapeSequences:
    def test_escaped_quote_inside_string(self):
        # Source JSON text:  "say \"hi\""
        assert parse(r'"say \"hi\""') == 'say "hi"'

    def test_escaped_backslash(self):
        # Source:  "a\\b"   →  "a\b" (one literal backslash)
        assert parse(r'"a\\b"') == "a\\b"

    def test_escaped_newline_and_tab(self):
        assert parse(r'"line1\nline2\ttabbed"') == "line1\nline2\ttabbed"

    def test_escaped_forward_slash(self):
        # \/ is legal JSON and decodes to plain /
        assert parse(r'"a\/b"') == "a/b"

    def test_escaped_carriage_return(self):
        assert parse(r'"x\ry"') == "x\ry"

    def test_escapes_inside_object_key(self):
        # Object keys are strings; escapes must be honored there too.
        assert parse(r'{"a\"b": 1}') == {'a"b': 1}

    def test_roundtrip_against_stdlib_json(self):
        """The fixed parser should agree with json.loads on a handful of docs
        whose only tricky feature is string escapes."""
        samples = [
            r'"hello \"world\""',
            r'"a\\b\\c"',
            r'{"k": "v\nwith newline"}',
            r'["x\/y", "no_escape"]',
        ]
        for s in samples:
            assert parse(s) == _stdjson.loads(s), f"mismatch on {s!r}"
