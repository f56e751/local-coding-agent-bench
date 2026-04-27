#!/usr/bin/env python3
"""Benchmark runner — Qwen vs Sonnet head-to-head.

Subcommands:
    prepare  <task> <model> <run>   Create isolated workspace, copy task files.
    run-qwen <workspace>            Invoke `claw` against Qwen, capture log.
    grade    <workspace>            Run pytest, produce result.json.
    summary  <results-dir>          Aggregate result.jsons into summary.md.

Sonnet is orchestrated by the parent Claude Code session (Agent tool); this
runner exposes `prepare` + `grade` so that both models share the same I/O shape.
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

ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"

CLAW = "/PublicSSD/minu/local-claude-project/claw-code/rust/target/release/claw"
QWEN_MODEL = "openai/qwen3-coder-agent:latest"
CLAW_TIMEOUT = 900  # seconds — matches plan's per-task limit
PYTEST_TIMEOUT = 120


def _task_src(task: str) -> Path:
    return TASKS_DIR / task


def prepare(task: str, model: str, run: str, output_dir: Path) -> Path:
    """Materialize a fresh workspace and return its path."""
    src = _task_src(task)
    if not src.exists():
        sys.exit(f"unknown task: {task}")
    ws = output_dir / model / f"{task}-run{run}"
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    # Copy starter + tests + PROMPT into workspace root.
    shutil.copytree(src / "starter", ws / "starter")
    shutil.copytree(src / "tests", ws / "tests")
    shutil.copy2(src / "PROMPT.md", ws / "PROMPT.md")
    return ws


def run_qwen(workspace: Path) -> dict:
    """Invoke claw non-interactively and return a metadata dict."""
    prompt_path = workspace / "PROMPT.md"
    prompt = prompt_path.read_text()

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
        "prompt",
        prompt,
    ]

    started = time.time()
    timed_out = False
    try:
        completed = subprocess.run(
            argv,
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=CLAW_TIMEOUT,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = e.stdout.decode() if e.stdout else ""
        stderr = e.stderr.decode() if e.stderr else ""
        exit_code = -1
    elapsed = time.time() - started

    (workspace / "run_stdout.log").write_text(stdout)
    (workspace / "run_stderr.log").write_text(stderr)

    meta = {
        "model": "qwen",
        "walltime_seconds": round(elapsed, 2),
        "exit_code": exit_code,
        "timed_out": timed_out,
    }
    (workspace / "run_meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def grade(workspace: Path) -> dict:
    """Run pytest inside the workspace and summarize results."""
    tests = workspace / "tests"
    if not tests.exists():
        sys.exit(f"no tests directory: {tests}")

    started = time.time()
    try:
        completed = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=PYTEST_TIMEOUT,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if e.stdout else ""
        stderr = e.stderr.decode() if e.stderr else ""
        exit_code = -1
    elapsed = time.time() - started

    # Parse pytest's short output — look for "N passed" / "N failed".
    passed = failed = errored = 0
    for token in stdout.splitlines()[-10:]:  # summary line is near the bottom
        if " passed" in token or " failed" in token or " error" in token:
            parts = token.replace(",", " ").split()
            for i, w in enumerate(parts):
                if w.isdigit() and i + 1 < len(parts):
                    nxt = parts[i + 1]
                    if nxt.startswith("passed"):
                        passed = int(w)
                    elif nxt.startswith("failed"):
                        failed = int(w)
                    elif nxt.startswith("error"):
                        errored = int(w)

    total = passed + failed + errored
    # Per-test pass/fail extraction from verbose output
    per_test = {}
    for line in stdout.splitlines():
        # example: tests/test_solution.py::test_foo PASSED
        if "PASSED" in line or "FAILED" in line or "ERROR" in line:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                verdict = parts[1] if parts[1] in ("PASSED", "FAILED", "ERROR") else None
                if verdict:
                    per_test[name] = verdict

    result = {
        "pass": failed == 0 and errored == 0 and passed > 0,
        "passed": passed,
        "failed": failed,
        "errored": errored,
        "total": total,
        "grading_walltime_seconds": round(elapsed, 2),
        "pytest_exit_code": exit_code,
        "per_test": per_test,
    }
    (workspace / "grade_stdout.log").write_text(stdout)
    (workspace / "grade_stderr.log").write_text(stderr)
    (workspace / "result.json").write_text(json.dumps(result, indent=2))
    return result


def summary(results_dir: Path) -> str:
    """Aggregate all result.json files into a markdown table."""
    rows: list[dict] = []
    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        if model_dir.name not in ("qwen", "sonnet"):
            continue
        for task_dir in sorted(model_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            rj = task_dir / "result.json"
            mj = task_dir / "run_meta.json"
            if not rj.exists():
                continue
            result = json.loads(rj.read_text())
            meta = json.loads(mj.read_text()) if mj.exists() else {}
            # task-run<N>
            name = task_dir.name
            task_id, _, run_part = name.partition("-run")
            rows.append({
                "model": model_dir.name,
                "task": task_id,
                "run": run_part or "1",
                "pass": result["pass"],
                "passed": result["passed"],
                "total": result["total"],
                "walltime": meta.get("walltime_seconds"),
                "timed_out": meta.get("timed_out", False),
            })

    # Build markdown
    lines = [
        "# Benchmark Results",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Per-run",
        "",
        "| Model | Task | Run | Pass | Tests | Walltime (s) | Notes |",
        "|-------|------|-----|------|-------|--------------|-------|",
    ]
    for r in rows:
        verdict = "✅" if r["pass"] else "❌"
        notes = "TIMEOUT" if r["timed_out"] else ""
        lines.append(
            f"| {r['model']} | {r['task']} | {r['run']} | {verdict} | "
            f"{r['passed']}/{r['total']} | {r['walltime']} | {notes} |"
        )

    # Aggregate pass@N per (model, task)
    from collections import defaultdict
    agg: dict[tuple[str, str], list[bool]] = defaultdict(list)
    tot_walltime: dict[str, float] = defaultdict(float)
    for r in rows:
        agg[(r["model"], r["task"])].append(r["pass"])
        if r["walltime"]:
            tot_walltime[r["model"]] += r["walltime"]

    lines += [
        "",
        "## Aggregated (pass rate per task)",
        "",
        "| Model | Task | Pass count | pass@N |",
        "|-------|------|------------|--------|",
    ]
    for (model, task), results in sorted(agg.items()):
        n = len(results)
        p = sum(results)
        at_least_one = "✅" if p > 0 else "❌"
        lines.append(f"| {model} | {task} | {p}/{n} | {at_least_one} |")

    lines += [
        "",
        "## Totals",
        "",
    ]
    for model, secs in sorted(tot_walltime.items()):
        lines.append(f"- **{model}** total wall time across runs: {secs:.1f}s")

    out = "\n".join(lines) + "\n"
    (results_dir / "summary.md").write_text(out)
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--task", required=True)
    prep.add_argument("--model", required=True, choices=["qwen", "sonnet"])
    prep.add_argument("--run", required=True)
    prep.add_argument("--output-dir", required=True, type=Path)

    rq = sub.add_parser("run-qwen")
    rq.add_argument("workspace", type=Path)

    g = sub.add_parser("grade")
    g.add_argument("workspace", type=Path)

    s = sub.add_parser("summary")
    s.add_argument("results_dir", type=Path)

    args = p.parse_args(argv)
    if args.cmd == "prepare":
        ws = prepare(args.task, args.model, args.run, args.output_dir)
        print(ws)
        return 0
    if args.cmd == "run-qwen":
        meta = run_qwen(args.workspace)
        print(json.dumps(meta, indent=2))
        return 0
    if args.cmd == "grade":
        result = grade(args.workspace)
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    if args.cmd == "summary":
        print(summary(args.results_dir))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
