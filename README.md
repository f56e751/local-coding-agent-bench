# Local Qwen3-Coder vs Claude Sonnet — Benchmark Study

A 4-day empirical study (2026-04-24 ~ 2026-04-27) comparing **Qwen3-Coder-30B-A3B-Instruct** running locally against **Claude Sonnet 4.6**, across multiple harnesses (Aider, mini-swe-agent, Claw Code) and benchmarks (custom 4-task, Aider polyglot, SWE-bench Verified).

**Hardware**: single RTX 4090 (24GB) · i9-11900K · 64GB RAM · Ubuntu 20.04.

📄 **Full report → [REPORT.md](./REPORT.md)** (495 lines, 7 sections including TL;DR, all 10 measurements, meta-analysis, and conclusions).

---

## Headline findings

| # | Setup | Pass | Sample |
|---|---|---|---|
| Sonnet 4.6 (Anthropic, mini-swe-agent) | SWE-bench Verified | **79.6%** | 500 |
| Qwen3-Coder-30B (Qwen official, OpenHands) | SWE-bench Verified | 50.0% | 500 |
| Qwen3-Coder-30B (ours, Aider whole format) | Aider polyglot Python | 26.5% | 34 |
| **Qwen3-Coder-30B (ours, Claw Code harness)** | **Aider polyglot Python** | **53.3%** | 15 |
| Qwen3-Coder-30B (ours, mini-swe-agent) | SWE-bench Verified | **10.0%** | 10 |
| **Qwen3-Coder-30B (ours, Claw Code harness)** | **SWE-bench Verified** | **0%** | 10 |

The results disprove the popular intuition that *"slapping the leaked Claude Code harness on Qwen closes the gap to Sonnet"*. The harness-effect is real but **bounded by training-distribution alignment** between model and tool grammar. On small/medium tasks it helps (+20 pp on Aider polyglot), on SWE-bench-scale tasks it hurts (Claw 0% vs mini-swe-agent 10%) because Qwen wasn't trained on Anthropic's `edit_file` exact-substring conventions.

See [REPORT.md §4 Meta analysis](./REPORT.md#4-메타-분석--왜-이렇게-되나) for the full causal model.

---

## Repo contents

```
.
├── REPORT.md                     # Main 495-line study
├── README.md                     # This file
├── benchmark/                    # Custom benchmark code + results
│   ├── runner.py                 # Custom 4-task driver (T1-T4)
│   ├── claw_polyglot.py          # Driver: Aider polyglot tasks via Claw Code
│   ├── claw_swebench.py          # Driver: SWE-bench Verified via Claw Code
│   ├── tasks/                    # Custom 4-task definitions
│   │   ├── t01-rotated-search/
│   │   ├── t02-merge-intervals/
│   │   ├── t03-json-parser-bug/
│   │   └── t04-cli-json-flag/
│   └── results/                  # All custom + Aider-polyglot-via-Claw runs
├── swebench-results/             # SWE-bench Verified runs
│   ├── b-10task/                 # mini-swe-agent + Qwen   (1/10)
│   ├── claw-10task/              # Claw 64K + Qwen         (0/10)
│   └── claw-10task-160k/         # Claw 160K + Qwen        (0/10)
├── logs/                         # swebench harness Docker eval logs
├── *.json                        # SWE-bench harness grading output
├── claw-env.sh                   # Shell env for Claw Code (Ollama routing)
├── mini-swe-config.yaml          # mini-swe-agent → Ollama routing
├── Modelfile.qwen3coder-agent    # Ollama Modelfile (64K context variant)
├── Modelfile.qwen3coder-128k     # Ollama Modelfile (128K context variant)
└── SETUP.md                      # How to reproduce the environment
```

---

## Reproducing

External dependencies (cloned but **not** vendored — see [SETUP.md](./SETUP.md)):

- [`instructkr/claw-code`](https://github.com/instructkr/claw-code) — Rust clean-room reimpl of Claude Code harness (the leak)
- [`Aider-AI/aider`](https://github.com/Aider-AI/aider) + [`Aider-AI/polyglot-benchmark`](https://github.com/Aider-AI/polyglot-benchmark)
- [`SWE-agent/mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) v2.2.8
- [`princeton-nlp/SWE-bench`](https://github.com/SWE-bench/SWE-bench) v4.1.0 (`pip install swebench`)
- [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) (built from source for 256K-context experiments)
- Ollama 0.21.2 for serving Qwen3-Coder-30B-A3B-Instruct (Q4_K_M GGUF)

The `.gitignore` excludes those clones, build artifacts, and venvs to keep the repo focused on the experiment artifacts (drivers, configs, results, report).

---

## License

MIT (see [LICENSE](./LICENSE)). Results / measurements are CC-BY-4.0 — please cite if reused.
