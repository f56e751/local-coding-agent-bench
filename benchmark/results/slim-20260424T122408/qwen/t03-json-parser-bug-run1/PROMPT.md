# Task T3 — Fix the JSON Parser

## Situation

`starter/parser.py` contains a small handwritten JSON parser. Most of its tests already pass, but the test suite under `tests/test_parser.py` has failing cases related to **backslash escape sequences inside string literals**. Your job is to fix the parser.

## What you must do

1. Read `starter/parser.py`. Identify the code path responsible for parsing string literals.
2. Make the parser handle JSON string escape sequences correctly. At minimum:
   - `\"` — literal double quote
   - `\\` — literal backslash
   - `\n` — newline (U+000A)
   - `\t` — tab (U+0009)
   - `\r` — carriage return (U+000D)
   - `\/` — forward slash (identity)
3. Keep every existing test green — do not regress the parts that already work.
4. Run `pytest tests/ -v` before declaring done.

## Rules

- Only modify files under `starter/`. Do not change the tests.
- Do not import `json` or any external library — write the escape handling in plain Python.
- Do not introduce new files.

## Hints

- The parser's string method currently walks until it sees a closing quote, ignoring `\`. This is the bug.
- JSON requires the return value to be the *unescaped* string (`\"` becomes `"`), not the raw source text.
