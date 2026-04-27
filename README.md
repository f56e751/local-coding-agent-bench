# Local Qwen3-Coder vs Claude Sonnet — Benchmark Study

A 4-day empirical study (2026-04-24 ~ 2026-04-27) testing whether the **leaked Claude Code harness** ("Claw") closes the performance gap between a local **Qwen3-Coder-30B-A3B-Instruct** and **Claude Sonnet 4.6** on real coding-agent benchmarks.

**Hardware**: single RTX 4090 (24GB) · i9-11900K · 64GB RAM · Ubuntu 20.04.
**Full report (Korean)**: 📄 [REPORT.md](./REPORT.md) — 495 lines, 10 measurements, full trajectory analysis.

---

## TL;DR — the story in 5 minutes

### 1. Baseline: how does the model perform natively?

Qwen3-Coder-30B-A3B-Instruct was published with a **50.0% pass@1** on SWE-bench Verified (Qwen team's official measurement, using the **OpenHands** scaffold at 500 turns — the harness Qwen was trained alongside).

That's our "vanilla" reference: **Qwen running in its native habitat**.

### 2. Hypothesis

> *"If we put the leaked Claude Code harness on top of Qwen, performance should jump significantly — possibly approaching Sonnet 4.6's 79.6% — because the harness does most of the heavy lifting in agentic coding."*

This was the popular intuition after the late-March 2026 npm-source-map leak that exposed Anthropic's full Claude Code TypeScript codebase (~512K lines): "*the engine isn't the moat; the harness is*". We wanted to put that hypothesis under direct measurement.

### 3. Benchmarks we used

Two benchmarks with deliberately different complexity profiles:

#### Aider Polyglot — small/medium scale
- 225 Exercism programming exercises across 6 languages (we used the Python subset: 34 tasks for the Aider-native run, 15 of those re-run via Claw for direct comparison)
- Each task is a **single-file algorithm/data-structure problem, 100–300 lines**
- Aider's scaffold uses the simplest possible edit format ("output the entire file")
- Good for measuring **raw coding capability + instruction following**

#### SWE-bench Verified — large/realistic scale
- 500 real GitHub issues from major Python projects (`astropy`, `django`, `sympy`, `scikit-learn`, …) — we ran the first 10 astropy instances
- Each task involves a **codebase of thousands of lines**, multi-file changes possible
- Solution is a `git diff` patch that must apply cleanly and pass the hidden test suite (graded inside Docker by the official `swebench.harness.run_evaluation`)
- Industry gold standard for coding-agent capability
- Standard scaffold = `mini-swe-agent` (the same one Anthropic uses to publish their numbers)

### 4. Results

| Setup | Benchmark | Pass | Source |
|---|---|---|---|
| **Qwen3-Coder vanilla** (OpenHands, *Qwen-native*) | SWE-bench Verified | **50.0%** | Qwen official (HF discussion) |
| Qwen3-Coder + Aider whole format | Aider polyglot Python (34) | 26.5% | ours |
| **Qwen3-Coder + Claw harness** (Claude Code leak) | Aider polyglot Python (15) | **53.3%** ⬆️ +20pp | ours |
| Qwen3-Coder + mini-swe-agent | SWE-bench Verified (10) | 10.0% | ours |
| **Qwen3-Coder + Claw harness** (Claude Code leak) | SWE-bench Verified (10) | **0%** ❌ | ours |
| **Sonnet 4.6 + mini-swe-agent** (Anthropic *co-trained*) | SWE-bench Verified | **79.6%** | Anthropic system card |

### 5. Hypothesis verdict — partially true, dramatically false

**Small tasks ✅ — hypothesis holds**
- Same model, same tasks, only the scaffold changed: Aider 26.5% → Claw **53.3%** (+20 pp, ×1.6)
- Strong evidence that the harness *can* lift outside-model performance.

**Large tasks ❌ — hypothesis collapses**
- Qwen with its native OpenHands harness: 50% on SWE-bench
- Qwen with Claude's leaked harness (Claw): **0%** (10/10 empty patches)
- The Claw harness didn't just fail to close the gap — it **lost ~50 percentage points** vs the native scaffold.

### 6. Why?

Claude Code's `edit_file` tool (used inside Claw) requires **exact substring matching**: `old_string` must appear *byte-for-byte* in the target file (whitespace and indentation included). Sonnet/Opus were trained on millions of these tool-call sequences during RLHF; the convention is baked into their weights.

Qwen3-Coder was trained with **different tool-call grammars** (Qwen-Agent / OpenHands / Hermes-style). When fed Claude's `edit_file`:

- **On small files** (Aider polyglot, ~150 lines): Qwen still keeps the entire file in active context, generates correct `old_string`, edits succeed → 53% pass.
- **On large files** (SWE-bench astropy `connect.py` ~800 lines, multi-turn exploration): once auto-compaction triggers, Qwen loses precise file content. Subsequent `edit_file` calls degenerate to no-ops with `old_string == new_string`, patches come out empty → 0% pass.

We verified this directly by inspecting trajectory traces — every "successful edit" Claw reported on SWE-bench was a no-op. Bumping context from 64K → 160K (via a custom-built `llama-server` with the CUDA toolchain installed through conda) made **zero difference**. Context wasn't the bottleneck. (We also tried 256K with MoE-expert offload to CPU RAM, but inference dropped to 3.7 tok/s, making any benchmark impractical.)

### 7. One-line conclusion

> **"Slap the leaked Claude Code harness on Qwen and you're Sonnet"** is a myth. Anthropic's real edge on SWE-bench isn't the harness in isolation — it's *co-training* the model and the harness together. That coupling doesn't transfer when you bolt the harness onto an outside model. The harness gives a meaningful boost on small/well-bounded tasks but breaks on large ones precisely because it expects a training-distribution match that Qwen doesn't have.

See [REPORT.md](./REPORT.md) for full trajectory analysis, the 256K-context experiment timeline, and counter-experiments we ran (different KV quantizations, half-vs-full MoE offload, etc.).

---

## Repo layout

```
.
├── REPORT.md                     # 495-line full study (Korean)
├── README.md                     # this file
├── benchmark/                    # Custom benchmark code + results
│   ├── runner.py                 # Custom 4-task driver (T1-T4)
│   ├── claw_polyglot.py          # Driver: Aider polyglot tasks via Claw Code
│   ├── claw_swebench.py          # Driver: SWE-bench Verified via Claw Code
│   ├── tasks/                    # Custom 4-task definitions
│   └── results/                  # All custom + Aider-polyglot-via-Claw runs
├── swebench-results/             # SWE-bench Verified runs (preds.json, trajectories, patches)
│   ├── b-10task/                 # mini-swe-agent + Qwen   → 1/10 (10%)
│   ├── claw-10task/              # Claw 64K + Qwen         → 0/10
│   └── claw-10task-160k/         # Claw 160K + Qwen        → 0/10
├── logs/                         # swebench harness Docker eval logs
├── claw-env.sh                   # Shell env for Claw Code (Ollama routing + wrapper)
├── mini-swe-config.yaml          # mini-swe-agent → Ollama routing
├── Modelfile.qwen3coder-agent    # Ollama Modelfile (64K context)
├── Modelfile.qwen3coder-128k     # Ollama Modelfile (128K context)
└── SETUP.md                      # How to reproduce the environment
```

## Reproducing

External dependencies (cloned but **not** vendored — re-fetch via [SETUP.md](./SETUP.md)):

- [`instructkr/claw-code`](https://github.com/instructkr/claw-code) — Rust clean-room reimpl of the leaked Claude Code harness
- [`Aider-AI/aider`](https://github.com/Aider-AI/aider) + [`Aider-AI/polyglot-benchmark`](https://github.com/Aider-AI/polyglot-benchmark)
- [`SWE-agent/mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) v2.2.8
- [`SWE-bench/SWE-bench`](https://github.com/SWE-bench/SWE-bench) v4.1.0
- [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) (built from source for the 256K-context experiment)
- Ollama 0.21.2 serving Qwen3-Coder-30B-A3B-Instruct (Q4_K_M GGUF)

## License

MIT (see [LICENSE](./LICENSE)). Measurements / results are CC-BY-4.0 — please cite if reused.
