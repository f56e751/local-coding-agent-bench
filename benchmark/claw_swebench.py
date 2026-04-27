#!/usr/bin/env python3
"""claw_swebench — drive Claw Code (leaked Claude Code harness clone) against
SWE-bench Verified tasks, capture model_patch via git diff, write preds.json
in the format expected by `swebench.harness.run_evaluation`.

Architecture:
  for each task:
    1. start a long-lived container from `swebench/sweb.eval.x86_64.<id>:latest`
       with --network host (so Claw inside can reach the host's Ollama on
       127.0.0.1:11434), claw binary bind-mounted into /usr/local/bin/claw,
       and the prompt file mounted in.
    2. exec Claw inside the container with the problem statement as a
       prompt.  Wall-time bounded.
    3. after Claw exits (or times out), `git add -A && git diff --cached`
       inside the container -> save as the model_patch.
    4. stop/remove the container.

We deliberately do NOT use mini-swe-agent's strict
"git diff > patch.txt && cat patch.txt" submission protocol — Qwen3-Coder
struggled with that.  Instead we capture the diff externally so the model can
just edit files normally, the way Claw Code is designed to be used.
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

CLAW_BIN = Path("/PublicSSD/minu/local-claude-project/claw-code/rust/target/release/claw")
DEFAULT_MODEL = "openai/qwen3-coder-256k"   # name is arbitrary for llama.cpp server
DEFAULT_TIMEOUT = 900  # seconds — wall-clock budget per task

# Target backend (llama.cpp server with 256K + MoE expert offload)
LLM_API_BASE = "http://127.0.0.1:8080/v1"
LLM_API_KEY = "llamacpp-local"


def _sg(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a docker command via `sg docker -c "..."` so the docker group is
    active (works around the non-relogin shell quirk on this machine)."""
    quoted = " ".join(_shell_quote(a) for a in cmd)
    full = ["sg", "docker", "-c", quoted]
    return subprocess.run(full, **kwargs)


def _shell_quote(s: str) -> str:
    # Conservative quoting for sh -c: wrap in single quotes, escape embedded singles.
    if not s:
        return "''"
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _instance_to_image(instance_id: str) -> str:
    # SWE-bench image naming: 'astropy__astropy-12907' -> 'astropy_1776_astropy-12907'
    img_id = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{img_id}:latest"


def _build_prompt(task: dict) -> str:
    return f"""# SWE-bench task: {task['instance_id']}

You are a software engineer working in the repository at `/testbed` (your current
working directory).  A bug has been described in the PR below — your job is to
fix it.  Use the file editing and bash tools available to you.

## Problem Description

{task['problem_statement']}

## Rules

- **MODIFY only source files** under `/testbed`.  Do NOT modify tests,
  configuration files (`pyproject.toml`, `setup.cfg`, `tox.ini`), or any
  reproduction scripts.
- Make the change as targeted and minimal as possible.
- You do NOT need to manually generate a git diff or patch — just edit the
  files directly with your tools.  Your changes will be captured automatically
  after you finish.
- When you believe the fix is complete, end your turn naturally (no special
  submission command needed).

## Suggested workflow

1. Briefly explore the relevant module / file referenced in the PR.
2. Understand the bug and what the desired fix is.
3. Make the minimal source change.
4. Optionally read back the modified file to confirm.
"""


def _ensure_container_dead(container: str) -> None:
    _sg(["docker", "rm", "-f", container], capture_output=True, text=True, check=False)


def run_task(task: dict, output_dir: Path, model: str, timeout: int) -> dict:
    instance_id = task["instance_id"]
    image = _instance_to_image(instance_id)
    workspace = output_dir / instance_id
    workspace.mkdir(parents=True, exist_ok=True)

    # Persist prompt for inspection
    prompt = _build_prompt(task)
    prompt_path = workspace / "PROMPT.md"
    prompt_path.write_text(prompt)

    container = f"clawswe-{instance_id.replace('__', '-').lower()}"
    _ensure_container_dead(container)

    started_total = time.time()

    # 1. Start long-lived container
    start_args = [
        "docker", "run", "-d",
        "--name", container,
        "--network", "host",
        "-v", f"{CLAW_BIN}:/usr/local/bin/claw:ro",
        "-v", f"{prompt_path}:/prompt.md:ro",
        "-e", f"OPENAI_BASE_URL={LLM_API_BASE}",
        "-e", f"OPENAI_API_KEY={LLM_API_KEY}",
        "-e", "HOME=/tmp",
        "-e", "TERM=dumb",
        "-w", "/testbed",
        image,
        "sleep", "1h",
    ]
    s = _sg(start_args, capture_output=True, text=True, check=False)
    if s.returncode != 0:
        return {
            "instance_id": instance_id,
            "model_patch": "",
            "error": f"docker start failed: {s.stderr[:500]}",
            "claw_seconds": 0,
            "claw_timed_out": False,
        }

    # 2. Exec Claw inside the container with the prompt.
    #    Use `timeout` so we cap wall time even if Claw hangs.
    exec_script = (
        "set -o pipefail; "
        f"timeout --kill-after=10 {timeout} "
        "/usr/local/bin/claw "
        f"--model {model} "
        "--permission-mode workspace-write "
        "--dangerously-skip-permissions "
        "--output-format text "
        "prompt \"$(cat /prompt.md)\""
    )
    started = time.time()
    timed_out = False
    try:
        e = _sg(
            ["docker", "exec", container, "bash", "-c", exec_script],
            capture_output=True, text=True,
            timeout=timeout + 60,
            check=False,
        )
        out, err, rc = e.stdout, e.stderr, e.returncode
        if rc == 124:  # timeout(1) sent SIGTERM
            timed_out = True
    except subprocess.TimeoutExpired as te:
        timed_out = True
        out = (te.stdout or b"").decode(errors="ignore") if isinstance(te.stdout, bytes) else (te.stdout or "")
        err = (te.stderr or b"").decode(errors="ignore") if isinstance(te.stderr, bytes) else (te.stderr or "")
        rc = -1
    elapsed = time.time() - started

    (workspace / "claw_stdout.log").write_text(out)
    (workspace / "claw_stderr.log").write_text(err)

    # 3. Capture the resulting diff — exclude Claw's own session/state dirs
    #    written into /testbed/.claw/ during the run.
    diff_script = (
        "cd /testbed && "
        "git add -A -- ':!.claw' ':!.cache' ':!__pycache__' 2>&1 >/dev/null && "
        "git diff --cached --no-color -- ':!.claw' ':!.cache' ':!__pycache__'"
    )
    g = _sg(
        ["docker", "exec", container, "bash", "-c", diff_script],
        capture_output=True, text=True, check=False,
    )
    patch = g.stdout if g.returncode == 0 else ""
    (workspace / "patch.diff").write_text(patch)

    # 4. Cleanup container
    _ensure_container_dead(container)

    total_elapsed = time.time() - started_total
    return {
        "instance_id": instance_id,
        "model_patch": patch,
        "claw_seconds": round(elapsed, 2),
        "claw_timed_out": timed_out,
        "claw_exit_code": rc,
        "patch_size": len(patch),
        "total_seconds": round(total_elapsed, 2),
    }


def load_dataset(subset: str = "verified", split: str = "test") -> list[dict]:
    """Load SWE-bench Verified via HuggingFace datasets."""
    from datasets import load_dataset as hf_load
    name = "princeton-nlp/SWE-bench_Verified" if subset == "verified" else f"princeton-nlp/SWE-bench_{subset.title()}"
    ds = hf_load(name, split=split)
    return list(ds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", default="verified")
    ap.add_argument("--split", default="test")
    ap.add_argument("--slice", default=None, help="e.g. '0:10'")
    ap.add_argument("--instance-ids", nargs="+", default=None,
                    help="explicit list of instance_ids to run (overrides --slice)")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset princeton-nlp/SWE-bench_{args.subset.title()} split={args.split} ...", flush=True)
    all_tasks = load_dataset(args.subset, args.split)

    if args.instance_ids:
        tasks = [t for t in all_tasks if t["instance_id"] in set(args.instance_ids)]
    elif args.slice:
        a, b = args.slice.split(":")
        tasks = all_tasks[int(a) if a else None : int(b) if b else None]
    else:
        tasks = all_tasks

    print(f"Running {len(tasks)} tasks; output={args.output}", flush=True)

    preds = {}
    for i, task in enumerate(tasks, 1):
        iid = task["instance_id"]
        print(f"\n[{i}/{len(tasks)}] {iid} ...", flush=True)
        try:
            res = run_task(task, args.output, args.model, args.timeout)
        except Exception as e:
            res = {"instance_id": iid, "model_patch": "", "error": str(e),
                   "claw_seconds": 0, "claw_timed_out": False, "patch_size": 0,
                   "total_seconds": 0}
        # SWE-bench harness expects this shape:
        preds[iid] = {
            "model_name_or_path": args.model,
            "instance_id": iid,
            "model_patch": res.get("model_patch", ""),
        }
        # Per-task meta
        (args.output / iid / "result.json").write_text(json.dumps(res, indent=2))
        verdict = "TIMEOUT" if res.get("claw_timed_out") else f"exit={res.get('claw_exit_code')}"
        print(f"  patch={res.get('patch_size', 0):>5d}B  claw={res.get('claw_seconds', 0):>5.0f}s  {verdict}", flush=True)
        # Periodic save
        (args.output / "preds.json").write_text(json.dumps(preds, indent=2))

    print(f"\nWrote {args.output / 'preds.json'}", flush=True)


if __name__ == "__main__":
    main()
