# Benchmark Results

Generated: 2026-04-24 21:58:49

## Per-run

| Model | Task | Run | Pass | Tests | Walltime (s) | Notes |
|-------|------|-----|------|-------|--------------|-------|
| qwen | t02-merge-intervals | 1 | ❌ | 19/20 | 900.01 | TIMEOUT |
| qwen | t03-json-parser-bug | 1 | ✅ | 19/19 | 217.8 |  |
| qwen | t04-cli-json-flag | 1 | ✅ | 9/9 | 900.01 | TIMEOUT |
| sonnet | t02-merge-intervals | 1 | ❌ | 19/20 | 146.21 |  |
| sonnet | t03-json-parser-bug | 1 | ✅ | 19/19 | 27.09 |  |
| sonnet | t04-cli-json-flag | 1 | ✅ | 9/9 | 42.98 |  |

## Aggregated (pass rate per task)

| Model | Task | Pass count | pass@N |
|-------|------|------------|--------|
| qwen | t02-merge-intervals | 0/1 | ❌ |
| qwen | t03-json-parser-bug | 1/1 | ✅ |
| qwen | t04-cli-json-flag | 1/1 | ✅ |
| sonnet | t02-merge-intervals | 0/1 | ❌ |
| sonnet | t03-json-parser-bug | 1/1 | ✅ |
| sonnet | t04-cli-json-flag | 1/1 | ✅ |

## Totals

- **qwen** total wall time across runs: 2017.8s
- **sonnet** total wall time across runs: 216.3s
