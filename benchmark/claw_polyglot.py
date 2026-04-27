#!/usr/bin/env python3
"""claw_polyglot — run Aider polyglot Python exercises through Claw Code.

For each exercise:
  1. copy starter (<task>.py + <task>_test.py + instructions) to a fresh workspace
  2. build a prompt from .docs/instructions.md (and .append.md)
  3. invoke `claw prompt "..."` (the Rust binary) against the local Ollama
  4. pytest; if fail, one feedback retry (matching Aider's --tries 2)
  5. record outcome

Produces per-task result.json and an aggregate summary.json.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

POLYGLOT = Path("/PublicSSD/minu/local-claude-project/aider/tmp.benchmarks/polyglot-benchmark/python/exercises/practice")
CLAW = "/PublicSSD/minu/local-claude-project/claw-code/rust/target/release/claw"
QWEN_MODEL = "openai/qwen3-coder-agent:latest"
CLAW_TIMEOUT = 600   # 10 min per claw invocation
PYTEST_TIMEOUT = 120  # pytest timeout per attempt

# Tasks Aider selected in the previous run (for fair comparison).
TASKS_34 = [
    "affine-cipher", "beer-song", "book-store", "bottle-song", "bowling",
    "connect", "dominoes", "dot-dsl", "food-chain", "forth",
    "go-counting", "grade-school", "grep", "hangman", "list-ops",
    "paasio", "phone-number", "pig-latin", "poker", "pov",
    "proverb", "react", "rest-api", "robot-name", "scale-generator",
    "sgf-parsing", "simple-linked-list", "transpose", "tree-building",
    "two-bucket", "variable-length-quantity", "wordy", "zebra-puzzle", "zipper",
]


def _read_instructions(task_dir: Path) -> str:
    parts = []
    for name in ("instructions.md", "instructions.append.md"):
        p = task_dir / ".docs" / name
        if p.exists():
            parts.append(p.read_text())
    return "\n\n".join(parts)


def _copy_workspace(task: str, dest: Path) -> Path:
    src = POLYGLOT / task
    if not src.exists():
        raise FileNotFoundError(src)
    dest.mkdir(parents=True, exist_ok=True)
    # Copy the starter .py and test file, plus instructions.
    for p in src.iterdir():
        if p.name.startswith(".meta"):
            continue  # hide reference solution
        if p.is_dir():
            shutil.copytree(p, dest / p.name, dirs_exist_ok=True)
        else:
            shutil.copy2(p, dest / p.name)
    return dest


def _build_prompt(task: str, workspace: Path, feedback: str | None = None) -> str:
    instructions = _read_instructions(POLYGLOT / task)
    starter_file = f"{task.replace('-', '_')}.py"
    test_file = f"{task.replace('-', '_')}_test.py"
    base = f"""# Task: {task}

Implement the solution in `{starter_file}` so that every test in `{test_file}` passes.

## Problem description

{instructions}

## Files

- Starter: `{starter_file}`  (edit this)
- Tests:   `{test_file}`  (do NOT edit; used for grading)

## Rules

- Only modify `{starter_file}`.  Do not edit the tests or create new files.
- Python stdlib only — no package installs.
- When you believe you are done, run `pytest {test_file} -x -q` and confirm green.
"""
    if feedback:
        base += "\n## Previous attempt failed — test feedback\n\n```\n" + feedback + "\n```\n\nFix the failures and try again.\n"
    return base


def _run_claw(workspace: Path, prompt: str) -> tuple[int, str, str, float, bool]:
    env = os.environ.copy()
    env["OPENAI_BASE_URL"] = "http://127.0.0.1:11434/v1"
    env["OPENAI_API_KEY"] = "ollama-local"
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_BASE_URL", None)
    argv = [
        CLAW,
        "--model", QWEN_MODEL,
        "--permission-mode", "workspace-write",
        "--dangerously-skip-permissions",
        "--output-format", "text",
        "prompt", prompt,
    ]
    started = time.time()
    timed_out = False
    try:
        p = subprocess.run(argv, cwd=workspace, env=env, capture_output=True, text=True, timeout=CLAW_TIMEOUT, check=False)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        out = (e.stdout or b"").decode(errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode(errors="ignore") if isinstance(e.stderr, bytes) else (e.stderr or "")
        rc = -1
    elapsed = time.time() - started
    return rc, out, err, elapsed, timed_out


def _run_pytest(workspace: Path, test_file: str) -> tuple[bool, str, float]:
    started = time.time()
    try:
        p = subprocess.run(
            ["python3", "-m", "pytest", test_file, "-x", "-q", "--tb=short"],
            cwd=workspace, capture_output=True, text=True, timeout=PYTEST_TIMEOUT, check=False,
        )
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode(errors="ignore") if isinstance(e.stderr, bytes) else (e.stderr or "")
        rc = -1
    elapsed = time.time() - started
    passed = rc == 0
    combined = (out + "\n" + err)[:4000]  # cap feedback size
    return passed, combined, elapsed


def run_task(task: str, outdir: Path) -> dict:
    test_file = f"{task.replace('-', '_')}_test.py"
    ws = outdir / task
    _copy_workspace(task, ws)

    # Try 1
    prompt1 = _build_prompt(task, ws)
    (ws / "PROMPT_try1.md").write_text(prompt1)
    rc1, out1, err1, t1, to1 = _run_claw(ws, prompt1)
    (ws / "claw_try1_stdout.log").write_text(out1)
    (ws / "claw_try1_stderr.log").write_text(err1)
    pass1, pytest_out1, pt1 = _run_pytest(ws, test_file)
    (ws / "pytest_try1.log").write_text(pytest_out1)

    result = {
        "task": task,
        "try1_claw_seconds": round(t1, 2),
        "try1_claw_timed_out": to1,
        "try1_pytest_seconds": round(pt1, 2),
        "try1_pass": pass1,
    }

    if pass1:
        result["try2_ran"] = False
        result["pass_1"] = True
        result["pass_2"] = True
        (ws / "result.json").write_text(json.dumps(result, indent=2))
        return result

    # Try 2 — feedback from pytest
    prompt2 = _build_prompt(task, ws, feedback=pytest_out1)
    (ws / "PROMPT_try2.md").write_text(prompt2)
    rc2, out2, err2, t2, to2 = _run_claw(ws, prompt2)
    (ws / "claw_try2_stdout.log").write_text(out2)
    (ws / "claw_try2_stderr.log").write_text(err2)
    pass2, pytest_out2, pt2 = _run_pytest(ws, test_file)
    (ws / "pytest_try2.log").write_text(pytest_out2)

    result["try2_ran"] = True
    result["try2_claw_seconds"] = round(t2, 2)
    result["try2_claw_timed_out"] = to2
    result["try2_pytest_seconds"] = round(pt2, 2)
    result["try2_pass"] = pass2
    result["pass_1"] = False
    result["pass_2"] = pass2
    (ws / "result.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--tasks", nargs="+", default=None,
                    help="specific task names; default uses Aider's 34 selected")
    ap.add_argument("--limit", type=int, default=None, help="limit to first N tasks")
    args = ap.parse_args()

    tasks = args.tasks or TASKS_34
    if args.limit:
        tasks = tasks[: args.limit]

    args.outdir.mkdir(parents=True, exist_ok=True)
    print(f"Running {len(tasks)} tasks; outdir={args.outdir}")

    rows = []
    overall_start = time.time()
    for i, task in enumerate(tasks, 1):
        t_start = time.time()
        print(f"\n[{i}/{len(tasks)}] {task} ...", flush=True)
        try:
            r = run_task(task, args.outdir)
        except Exception as e:
            print(f"  ERROR: {e}")
            r = {"task": task, "error": str(e), "pass_1": False, "pass_2": False}
        elapsed = time.time() - t_start
        p1 = "✅" if r.get("pass_1") else "❌"
        p2 = "✅" if r.get("pass_2") else "❌"
        print(f"  try1={p1} try2={p2}  ({elapsed:.1f}s)")
        rows.append(r)

    total = time.time() - overall_start
    n = len(rows)
    pass1_count = sum(1 for r in rows if r.get("pass_1"))
    pass2_count = sum(1 for r in rows if r.get("pass_2"))

    summary = {
        "model": QWEN_MODEL,
        "scaffold": "claw-code",
        "num_tasks": n,
        "pass_rate_1": round(100.0 * pass1_count / n, 1) if n else 0,
        "pass_rate_2": round(100.0 * pass2_count / n, 1) if n else 0,
        "pass_num_1": pass1_count,
        "pass_num_2": pass2_count,
        "total_wall_seconds": round(total, 1),
        "seconds_per_task": round(total / n, 1) if n else 0,
        "rows": rows,
    }
    (args.outdir / "summary.json").write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 60)
    print(f"TOTAL: {n} tasks | pass@1 {pass1_count}/{n} ({summary['pass_rate_1']}%) | pass@2 {pass2_count}/{n} ({summary['pass_rate_2']}%)")
    print(f"Wall time: {total:.1f}s  (~{total/60:.1f} min)  avg {total/n:.1f}s/task")
    print("=" * 60)


if __name__ == "__main__":
    main()
