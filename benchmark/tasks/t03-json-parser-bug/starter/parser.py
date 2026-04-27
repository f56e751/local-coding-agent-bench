"""Tiny JSON parser.

Supports:
- null / true / false
- integers and floating-point numbers (no scientific notation)
- strings (double-quoted)  ← has a known bug around escape sequences
- arrays and objects

This module is intended to be importable as `from parser import parse`.
"""
from __future__ import annotations


class JSONDecodeError(ValueError):
    """Raised when the input is not valid JSON per this parser's grammar."""


def parse(text: str):
    """Parse `text` and return the corresponding Python value."""
    p = _Parser(text)
    value = p._value()
    p._skip_ws()
    if p.pos < len(p.text):
        raise JSONDecodeError(f"trailing garbage at position {p.pos}")
    return value


class _Parser:
    __slots__ = ("text", "pos")

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    # -- helpers --

    def _skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def _peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def _expect(self, ch):
        if self._peek() != ch:
            raise JSONDecodeError(f"expected {ch!r} at position {self.pos}")
        self.pos += 1

    # -- grammar --

    def _value(self):
        self._skip_ws()
        c = self._peek()
        if c is None:
            raise JSONDecodeError("unexpected end of input")
        if c == "{":
            return self._object()
        if c == "[":
            return self._array()
        if c == '"':
            return self._string()
        if c == "-" or c.isdigit():
            return self._number()
        if self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        if self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        if self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        raise JSONDecodeError(f"unexpected character {c!r} at position {self.pos}")

    def _string(self):
        self._expect('"')
        start = self.pos
        # BUG: naively scans for a closing quote without interpreting backslash
        # escapes. This means the return value includes the raw backslash
        # sequences rather than their unescaped forms, and \" prematurely ends
        # the string.
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1
        if self.pos >= len(self.text):
            raise JSONDecodeError("unterminated string literal")
        raw = self.text[start:self.pos]
        self.pos += 1  # closing quote
        return raw

    def _number(self):
        start = self.pos
        if self._peek() == "-":
            self.pos += 1
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        is_float = False
        if self._peek() == ".":
            is_float = True
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        token = self.text[start : self.pos]
        return float(token) if is_float else int(token)

    def _array(self):
        self._expect("[")
        out = []
        self._skip_ws()
        if self._peek() == "]":
            self.pos += 1
            return out
        while True:
            out.append(self._value())
            self._skip_ws()
            c = self._peek()
            if c == ",":
                self.pos += 1
                continue
            if c == "]":
                self.pos += 1
                return out
            raise JSONDecodeError(f"expected ',' or ']' at position {self.pos}")

    def _object(self):
        self._expect("{")
        out = {}
        self._skip_ws()
        if self._peek() == "}":
            self.pos += 1
            return out
        while True:
            self._skip_ws()
            key = self._string()
            self._skip_ws()
            self._expect(":")
            out[key] = self._value()
            self._skip_ws()
            c = self._peek()
            if c == ",":
                self.pos += 1
                continue
            if c == "}":
                self.pos += 1
                return out
            raise JSONDecodeError(f"expected ',' or '}}' at position {self.pos}")
