# 로컬 Qwen3-Coder vs Claude Sonnet — 벤치마크 연구

**유출된 Claude Code 하네스("Claw")**를 로컬 **Qwen3-Coder-30B-A3B-Instruct**에 씌우면 **Claude Sonnet 4.6**과의 성능 격차가 메워질까? 4일간(2026-04-24 ~ 04-27) 실측한 연구.

**하드웨어**: RTX 4090 24GB · i9-11900K · 64GB RAM · Ubuntu 20.04
**상세 리포트**: 📄 [REPORT.md](./REPORT.md) — 495줄, 10개 측정, 전체 trajectory 분석

---

## TL;DR — 5분 요약

### 1. 베이스라인: 모델은 native 환경에서 얼마나 잘하나?

Qwen3-Coder-30B-A3B-Instruct는 SWE-bench Verified에서 **50.0% pass@1**로 공식 발표됨 (Qwen 팀이 OpenHands 스캐폴드 + 500턴으로 측정 — Qwen이 같이 학습한 하네스).

이게 우리의 "vanilla 기준선" — **Qwen이 자기 native 환경에서 돌 때**의 진짜 실력.

### 2. 가설

> *"유출된 Claude Code 하네스를 Qwen에 씌우면 성능이 큰 폭 상승할 것 — 어쩌면 Sonnet 4.6의 79.6%에 근접할지도. 에이전틱 코딩에서 정말 무거운 일은 하네스가 하는 거니까."*

2026년 3월 말 npm 소스맵 유출로 Anthropic의 Claude Code 전체 TypeScript 코드(~512K줄)가 공개된 직후 커뮤니티에 퍼진 직관: **"엔진(모델)이 아니라 하네스가 진짜 moat다"**. 이걸 직접 측정으로 검증.

### 3. 사용한 벤치마크

복잡도가 의도적으로 다른 두 벤치마크를 골랐음:

#### Aider Polyglot — 작은/중간 규모
- 6개 언어로 된 Exercism 코딩 과제 225개 (Python 서브셋만 사용: Aider-native 측정 34개, Claw 비교용 15개)
- 각 task는 **단일 파일 알고리즘/자료구조 문제, 100~300줄**
- Aider 자체 스캐폴드는 가장 단순한 편집 형식 사용 ("파일 전체를 다시 출력")
- **순수 코딩 능력 + 명령 수행** 측정에 적합

#### SWE-bench Verified — 크고 현실적인 규모
- 주요 Python 프로젝트(`astropy`, `django`, `sympy`, `scikit-learn` 등)의 실제 GitHub issue 500개 — 우리는 첫 10개 astropy 인스턴스 사용
- 각 task는 **수천~수만 줄 codebase**, 멀티파일 변경 잠재
- 정답은 깨끗하게 적용되고 hidden test suite를 통과하는 `git diff` 패치 (Docker 안에서 공식 `swebench.harness.run_evaluation`으로 자동 채점)
- **코딩 에이전트 업계 표준 벤치마크**
- 표준 측정 스캐폴드 = `mini-swe-agent` (Anthropic이 자기 점수 발표할 때 쓰는 그 도구)

### 4. 결과

| 셋업 | 벤치마크 | Pass | 출처 |
|---|---|---|---|
| **Qwen3-Coder vanilla** (OpenHands, *Qwen-native*) | SWE-bench Verified | **50.0%** | Qwen 공식 (HF discussion) |
| Qwen3-Coder + Aider whole format | Aider polyglot Python (34) | 26.5% | 우리 측정 |
| **Qwen3-Coder + Claw 하네스** (Claude Code 유출본) | Aider polyglot Python (15) | **53.3%** ⬆️ +20pp | 우리 측정 |
| Qwen3-Coder + mini-swe-agent | SWE-bench Verified (10) | 10.0% | 우리 측정 |
| **Qwen3-Coder + Claw 하네스** (Claude Code 유출본) | SWE-bench Verified (10) | **0%** ❌ | 우리 측정 |
| **Sonnet 4.6 + mini-swe-agent** (Anthropic, *co-training*) | SWE-bench Verified | **79.6%** | Anthropic system card |

### 5. 가설 평가 — 부분 사실, 부분 극적 거짓

**작은 task ✅ — 가설 성립**
- 같은 모델, 같은 task, 스캐폴드만 변경: Aider 26.5% → Claw **53.3%** (+20pp, ×1.6배)
- 하네스가 외부 모델 성능을 끌어올릴 수 있다는 강한 증거.

**큰 task ❌ — 가설 붕괴**
- Qwen + 자기 native OpenHands: SWE-bench 50%
- Qwen + Claude의 유출 하네스 (Claw): **0%** (10/10 빈 patch)
- Claw 하네스가 격차 메우긴커녕 native 스캐폴드 대비 **약 50%p 깎아먹음**.

### 6. 왜?

Claude Code의 `edit_file` 도구(Claw 안에서 사용)는 **정확한 substring 매칭**을 요구함: `old_string`이 대상 파일에 *바이트 단위로 일치*해야 함 (whitespace, indentation 한 글자도 안 어긋남). Sonnet/Opus는 RLHF 단계에서 이런 도구 호출 시퀀스를 **수백만 회** 학습 — 컨벤션이 가중치에 박혀 있음.

Qwen3-Coder는 **다른 도구 호출 grammar**(Qwen-Agent / OpenHands / Hermes-style)로 학습됨. Claude의 `edit_file`을 받았을 때:

- **작은 파일** (Aider polyglot, ~150줄)에선: Qwen이 파일 전체를 active 컨텍스트에 유지 → 정확한 `old_string` 생성 → edit 성공 → 53% pass.
- **큰 파일** (SWE-bench astropy `connect.py` ~800줄, 멀티턴 탐색)에선: auto-compaction 한 번 발동하면 Qwen이 파일의 정확한 내용을 잃어버림 → 그 다음 `edit_file` 호출이 `old_string == new_string` 같은 무효 인자로 변질 → patch가 빈 채로 나옴 → **0% pass**.

trajectory 직접 분석으로 검증함 — Claw가 SWE-bench에서 "edit 성공"으로 보고한 것 모두 사실은 no-op이었음. 컨텍스트를 64K → 160K로 늘려도 (conda로 CUDA toolchain 설치해서 자가 빌드한 `llama-server`로) **결과 동일**. 컨텍스트가 병목이 아니었음. (256K도 시도했지만 MoE expert를 CPU RAM에 오프로드해야 해서 추론 속도가 3.7 tok/s로 떨어져 측정 자체 불가.)

### 7. 한 줄 결론

> **"유출된 Claude Code 하네스 Qwen에 씌우면 Sonnet 된다"는 환상.** Anthropic의 진짜 SWE-bench 경쟁력은 하네스 단독이 아니라 **모델과 하네스를 같이 학습시킨(co-training) 효과**. 그 결합은 외부 모델에 하네스만 옮겨 끼울 때 따라오지 않음. 하네스는 작고 잘 정의된 task에선 의미 있는 부스트를 주지만, 큰 task에선 학습 분포 매칭 부재가 노출돼 오히려 깎임.

전체 trajectory 분석, 256K-컨텍스트 실험 타임라인, 추가 대조 실험(다른 KV 양자화, half vs full MoE 오프로드 등)은 [REPORT.md](./REPORT.md) 참고.

---

## Repo 구조

```
.
├── REPORT.md                     # 495줄 본 연구 보고서 (한국어)
├── README.md                     # 이 파일
├── benchmark/                    # 자작 벤치마크 코드 + 결과
│   ├── runner.py                 # 자작 4-task 실행기 (T1-T4)
│   ├── claw_polyglot.py          # Aider polyglot task를 Claw로 돌리는 driver
│   ├── claw_swebench.py          # SWE-bench Verified를 Claw로 돌리는 driver
│   ├── tasks/                    # 자작 4-task 정의
│   └── results/                  # 자작 + Aider-via-Claw 모든 실행 결과
├── swebench-results/             # SWE-bench Verified 실행 (preds.json, trajectory, patch)
│   ├── b-10task/                 # mini-swe-agent + Qwen   → 1/10 (10%)
│   ├── claw-10task/              # Claw 64K + Qwen         → 0/10
│   └── claw-10task-160k/         # Claw 160K + Qwen        → 0/10
├── logs/                         # swebench harness Docker 채점 로그
├── claw-env.sh                   # Claw Code용 환경변수 + wrapper 함수
├── mini-swe-config.yaml          # mini-swe-agent → Ollama 라우팅 설정
├── Modelfile.qwen3coder-agent    # Ollama Modelfile (64K 컨텍스트)
├── Modelfile.qwen3coder-128k     # Ollama Modelfile (128K 컨텍스트)
└── SETUP.md                      # 환경 재현 가이드
```

## 재현 방법

외부 의존성들 (clone하지만 vendoring은 안 함 — [SETUP.md](./SETUP.md) 참고해서 재설치):

- [`instructkr/claw-code`](https://github.com/instructkr/claw-code) — Claude Code 유출 하네스의 Rust clean-room 재구현
- [`Aider-AI/aider`](https://github.com/Aider-AI/aider) + [`Aider-AI/polyglot-benchmark`](https://github.com/Aider-AI/polyglot-benchmark)
- [`SWE-agent/mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) v2.2.8
- [`SWE-bench/SWE-bench`](https://github.com/SWE-bench/SWE-bench) v4.1.0
- [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) (256K 컨텍스트 실험용 자가 빌드)
- Ollama 0.21.2 + Qwen3-Coder-30B-A3B-Instruct (Q4_K_M GGUF)

## 라이선스

MIT (코드/문서 — [LICENSE](./LICENSE) 참고). 측정 결과/데이터는 CC-BY-4.0 — 재사용 시 인용 부탁드립니다.
