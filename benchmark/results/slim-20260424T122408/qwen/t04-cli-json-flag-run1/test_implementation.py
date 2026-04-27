#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STARTER = ROOT / "starter"
CLI = STARTER / "wordcount.py"

SAMPLE = "Hello world\nThis is a sample file.\nThree lines here.\n"
SAMPLE_LINES = 3
SAMPLE_WORDS = 10
SAMPLE_CHARS = len(SAMPLE)

def run(args, input_text=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(STARTER),
        capture_output=True,
        text=True,
        input=input_text,
    )

# Test 1: Default behavior (should be text)
print("Test 1: Default behavior")
r = run([ "-", ], input_text=SAMPLE)
print("Return code:", r.returncode)
print("Output:", repr(r.stdout))
assert r.returncode == 0
assert f"Lines: {SAMPLE_LINES}" in r.stdout
print("✓ Default behavior works")

# Test 2: Explicit text format
print("\nTest 2: Explicit text format")
r = run([ "-", "--output-format", "text"], input_text=SAMPLE)
print("Return code:", r.returncode)
print("Output:", repr(r.stdout))
assert r.returncode == 0
assert f"Lines: {SAMPLE_LINES}" in r.stdout
print("✓ Explicit text format works")

# Test 3: JSON format with space-separated
print("\nTest 3: JSON format (space-separated)")
r = run([ "-", "--output-format", "json"], input_text=SAMPLE)
print("Return code:", r.returncode)
print("Output:", repr(r.stdout))
assert r.returncode == 0
data = json.loads(r.stdout)
assert data == {"lines": SAMPLE_LINES, "words": SAMPLE_WORDS, "chars": SAMPLE_CHARS}
print("✓ JSON format (space-separated) works")

# Test 4: JSON format with equals form
print("\nTest 4: JSON format (equals form)")
r = run([ "-", "--output-format=json"], input_text=SAMPLE)
print("Return code:", r.returncode)
print("Output:", repr(r.stdout))
assert r.returncode == 0
data = json.loads(r.stdout)
assert data["lines"] == SAMPLE_LINES
print("✓ JSON format (equals form) works")

# Test 5: Invalid format rejection
print("\nTest 5: Invalid format rejection")
r = run([ "-", "--output-format", "xml"], input_text=SAMPLE)
print("Return code:", r.returncode)
print("Stderr:", repr(r.stderr))
assert r.returncode != 0
print("✓ Invalid format properly rejected")

print("\nAll tests passed!")