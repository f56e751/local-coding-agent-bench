# Task T4 — Add `--output-format json` to the wordcount CLI

## Project layout

```
starter/
  wordcount.py     # entry point (argparse)
  stats.py         # line / word / character counting
  formatter.py     # currently only text output
tests/
  test_cli.py      # integration tests (invoke CLI via subprocess)
```

## Current state

`wordcount.py <file>` reads a file (or stdin if `<file>` is `-`) and prints human-readable line/word/character counts to stdout. Existing text-output tests pass.

## Your task

Add a new CLI flag **`--output-format {text,json}`** (default `text`) that:

1. When `json`, prints the stats as a single-line JSON document to stdout:
   `{"lines": <int>, "words": <int>, "chars": <int>}`
2. When `text` (default), keeps the existing human-readable behavior byte-for-byte.
3. When given any other value, argparse should reject the argument (non-zero exit).
4. Both `--output-format json` and `--output-format=json` must work (standard argparse behavior).

## Rules

- Only modify files under `starter/`. Do not edit the tests.
- All existing tests must keep passing. The JSON tests are new and currently fail.
- Python stdlib only — use `json` module for serialization.
- Don't rename files or symbols; the tests import by current paths.

## Verify

Run `pytest tests/ -v` from the workspace root and confirm everything is green.
