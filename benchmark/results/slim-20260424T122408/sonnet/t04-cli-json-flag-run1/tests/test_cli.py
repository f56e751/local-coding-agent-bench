"""T4 grader — invokes the CLI via subprocess and validates output."""
import json as _json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARTER = ROOT / "starter"
CLI = STARTER / "wordcount.py"


SAMPLE = "Hello world\nThis is a sample file.\nThree lines here.\n"
SAMPLE_LINES = 3
SAMPLE_WORDS = 10
SAMPLE_CHARS = len(SAMPLE)


def _run(args, input_text=None, timeout=10):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(STARTER),  # so `from stats import count` resolves
        capture_output=True,
        text=True,
        timeout=timeout,
        input=input_text,
    )


def _write_sample():
    f = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt")
    f.write(SAMPLE)
    f.close()
    return f.name


# ==== Existing behavior — must stay green ====

def test_text_default():
    path = _write_sample()
    r = _run([path])
    assert r.returncode == 0, r.stderr
    assert f"Lines: {SAMPLE_LINES}" in r.stdout
    assert f"Words: {SAMPLE_WORDS}" in r.stdout
    assert f"Chars: {SAMPLE_CHARS}" in r.stdout


def test_text_explicit():
    path = _write_sample()
    r = _run([path, "--output-format", "text"])
    assert r.returncode == 0, r.stderr
    assert f"Lines: {SAMPLE_LINES}" in r.stdout


def test_stdin_text():
    r = _run(["-"], input_text=SAMPLE)
    assert r.returncode == 0, r.stderr
    assert f"Words: {SAMPLE_WORDS}" in r.stdout


# ==== New behavior — currently failing; must be made to pass ====

def test_json_space_separated():
    path = _write_sample()
    r = _run([path, "--output-format", "json"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = _json.loads(r.stdout)
    assert data == {"lines": SAMPLE_LINES, "words": SAMPLE_WORDS, "chars": SAMPLE_CHARS}


def test_json_equals_form():
    path = _write_sample()
    r = _run([path, "--output-format=json"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = _json.loads(r.stdout)
    assert data["lines"] == SAMPLE_LINES


def test_json_stdin():
    r = _run(["-", "--output-format", "json"], input_text="one two three\nfour five\n")
    assert r.returncode == 0, r.stderr
    data = _json.loads(r.stdout)
    assert data == {"lines": 2, "words": 5, "chars": 24}


def test_invalid_format_rejected():
    path = _write_sample()
    r = _run([path, "--output-format", "xml"])
    assert r.returncode != 0, "expected argparse to reject unsupported format"


def test_json_empty_file():
    f = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt")
    f.close()
    r = _run([f.name, "--output-format", "json"])
    assert r.returncode == 0, r.stderr
    data = _json.loads(r.stdout)
    assert data == {"lines": 0, "words": 0, "chars": 0}


def test_json_output_is_single_line():
    path = _write_sample()
    r = _run([path, "--output-format", "json"])
    assert r.returncode == 0, r.stderr
    # One line of JSON + optional trailing newline from print()
    body = r.stdout.rstrip("\n")
    assert "\n" not in body, f"expected a single-line JSON document, got: {r.stdout!r}"
