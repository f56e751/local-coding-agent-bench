#!/usr/bin/env python3
"""wordcount — report line, word, and character counts for a text file.

Usage:
  wordcount.py <file>       # file path, or '-' for stdin
  wordcount.py <file> --output-format {text,json}   ← you are adding this
"""
from __future__ import annotations

import argparse
import sys

from stats import count
from formatter import format_text, format_json


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wordcount",
        description="Count lines, words, and characters in a text file.",
    )
    parser.add_argument("file", help="path to input file, or '-' for stdin")
    parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args(argv)

    if args.file == "-":
        text = sys.stdin.read()
    else:
        with open(args.file, "r") as f:
            text = f.read()

    stats = count(text)
    if args.output_format == "json":
        print(format_json(stats))
    else:
        print(format_text(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
