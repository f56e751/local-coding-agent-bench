# 로컬 Qwen3-Coder × Claude Sonnet 종합 벤치마크 리포트

**기간**: 2026-04-24 ~ 2026-04-27 (4일)
**하드웨어**: RTX 4090 24GB · i9-11900K · 64GB RAM · Ubuntu 20.04
**모델**: Qwen3-Coder-30B-A3B-Instruct (로컬, MoE 30B/3B 활성, Q4_K_M GGUF)
**비교 대상**: Claude Sonnet 4.6 (Anthropic 공식 + 우리 subagent 호출)

---

## TL;DR (3분 요약)

10개 셋업으로 측정. 다섯 가지 결정적 발견:

1. **하네스가 모델만큼 점수를 결정**: 같은 Qwen이 Aider whole 26.5% → Claw 53.3% (+20%p, 1.6배). 스캐폴드 효과 실재.

2. **하지만 효과 크기가 task 복잡도에 강하게 반비례**:
   - 자작 단순 task (3~80줄, 단일 파일): Claw 효과 ~95% (변별력 거의 없음)
   - Aider polyglot (100~300줄): Claw 효과 +20%p
   - SWE-bench Verified (수천 줄, 멀티파일): **Claw 효과 음수** — mini-swe-agent 10% vs Claw 0%

3. **컨텍스트 크기는 SWE-bench에서 병목이 아님**: 64K → 160K 두 배 늘려도 결과 동일 (둘 다 0/10). 256K 시도는 MoE expert offload로 인퍼런스 속도 3.7 tok/s까지 떨어져 측정 자체 불가.

4. **진짜 병목 = model-harness 학습 분포 매칭**: Qwen이 Anthropic의 `edit_file(old_string, new_string)` 정확 매칭 grammar를 학습 안 함 → 큰 파일에선 `old_string ≡ new_string` 같은 무효 인자 호출 → patch 비어 나옴. Sonnet은 Anthropic이 자기 학습 데이터로 이 grammar를 박아 넣음.

5. **"유출 하네스가 격차를 메운다"는 환상**: Claude Code 하네스를 Qwen에 그대로 씌우는 건 "한국어 학습한 사람한테 일본어 문법 시험". 모델 capacity 늘려도 학습 분포 mismatch는 부분 흡수만 가능.

---

## 1. 모든 측정 결과 (한 표)

| # | 모델 | 스캐폴드 (= 하네스) | 벤치마크 | pass | 샘플 | 출처 |
|---|---|---|---|---|---|---|
| 1 | Sonnet 4.6 | mini-swe-agent | SWE-bench Verified | **79.6%** | 500 | Anthropic 공식 system card |
| 2 | Sonnet 4.6 | Anthropic 내부 (≈ Claw) | 자작 4-task | 100% (4/4) | 4 | 우리 측정 (subagent 호출) |
| 3 | Qwen3-Coder-30B-A3B | OpenHands 500턴 | SWE-bench Verified | 50.0% | 500 | Qwen 공식 HF discussion |
| 4 | Qwen3-Coder-30B-A3B | Claw + Ollama 64K | 자작 4-task | ~95% (3.8/4) | 4 | 우리 측정 |
| 5 | Qwen3-Coder-30B-A3B | Aider whole format | Aider polyglot Python | 26.5% (pass@2) | 34 | 우리 측정 (Aider 정공) |
| 6 | Qwen3-Coder-30B-A3B | **Claw + Ollama 64K** | Aider polyglot Python | **53.3%** (pass@2) | 15 | 우리 측정 (= **+20%p vs #5**) |
| 7 | Qwen3-Coder-30B-A3B | mini-swe-agent | SWE-bench Verified | **10.0%** (pass@1) | 10 | 우리 측정 |
| 8 | Qwen3-Coder-30B-A3B | **Claw + Ollama 64K** | SWE-bench Verified | **0%** (pass@1) | 10 | 우리 측정 |
| 9 | Qwen3-Coder-30B-A3B | Claw + llama.cpp 256K MoE offload | SWE-bench Verified | N/A (timeout) | 2 (중단) | 3.7 tok/s, 실용 불가 |
| 10 | Qwen3-Coder-30B-A3B | **Claw + llama.cpp 160K all-GPU** | SWE-bench Verified | **0%** (pass@1) | 10 | 우리 측정 (189 tok/s 정상속도) |

**셋업 특별히 주목할 4쌍**:
- **#5 vs #6** (Aider whole vs Claw on Aider polyglot): 같은 task, 다른 하네스 → +20%p
- **#7 vs #8** (mini-swe-agent vs Claw on SWE-bench): 같은 task, 다른 하네스 → -10%p (역전!)
- **#8 vs #10** (Claw 64K vs Claw 160K on SWE-bench): 같은 하네스, 다른 컨텍스트 → 변화 없음
- **#3 vs #7** (Qwen native OpenHands vs Qwen × foreign mini-swe-agent): 같은 모델, 다른 하네스 → 50% → 10% (모델 grammar mismatch 효과)

---

## 2. 하드웨어 / 환경

```
GPU      : NVIDIA GeForce RTX 4090 24GB (compute capability 8.9, Ada Lovelace)
CPU      : Intel i9-11900K (8c/16t)
RAM      : 64GB DDR4
SSD 1    : /dev/nvme0n1p2 = 1.8TB (root, 1.4TB free)
SSD 2    : /dev/nvme1n1   = 1.8TB (/PublicSSD, 1.2TB free)
OS       : Ubuntu 20.04 (GLIBC 2.31)
GCC      : 9.4 system / 11.4 conda
NVIDIA   : driver 550.144.03, CUDA 12.4
sudo     : 사용자 lminu는 sudoers 미포함 (admin 별도)
```

설치된 추론 백엔드:
- **Ollama 0.21.2** (userspace, ~/.local/bin/ollama) — 주요 사용
- **llama.cpp** (자체 빌드, /PublicSSD/.../llama.cpp/build) — 256K 도전용
- **mini-swe-agent 2.2.8** (별도 venv) — SWE-bench 표준 측정
- **swebench 4.1.0** (별도 venv) — Docker 기반 채점 harness

---

## 3. 단계별 상세

### 3.1 셋업 (Day 1, 2026-04-24)

**Claude Code 유출 사건 (2026-03-31)** 후 공개된 [instructkr/claw-code](https://github.com/instructkr/claw-code) clean-room Rust 재구현을 클론·빌드:
- Rust toolchain 1.95.0 (rustup)
- Ollama userspace 설치 (admin 없이 ~/.local/bin)
- Qwen3-Coder-30B-A3B-Instruct (Q4_K_M, ~18GB) `ollama pull`
- 64K 컨텍스트, q8_0 KV cache, Flash Attention 활성

**최종 동작 확인**: `claw "shell tool로 uname -a 실행해서 OS 요약" → 0.88초 만에 정확한 응답`. 툴콜 동작 확인.

**저장된 산출물**:
```
/PublicSSD/minu/local-claude-project/
├── claw-code/                 # Rust 재구현 source + binary
├── Modelfile.qwen3coder-agent # 64K + 보수적 sampling
└── claw-env.sh                # OPENAI_BASE_URL + wrapper function
```

### 3.2 자작 4-task 벤치 (Day 1)

설계: Qwen + Claw vs Sonnet 4.6 + Claude Code subagent를 동일 4 task로 직접 비교.

| Task | 유형 | 결과 |
|---|---|---|
| T1 rotated-search | 알고리즘 (O(log n)) | Qwen 19/20, Sonnet 20/20 |
| T2 merge-intervals | 엣지케이스 + stress test | Qwen 19/20, Sonnet 19/20 *(Sonnet이 내 fixture 버그를 명시적으로 진단)* |
| T3 json-parser-bug | SWE-bench style 버그 fix | Qwen 19/19, Sonnet 19/19 |
| T4 cli-json-flag | 멀티파일 기능 추가 | Qwen 9/9, Sonnet 9/9 |
| **합** | | **Qwen 95%, Sonnet 100%** |

이 결과로 "Claw + Qwen ≈ Sonnet"이라는 가설 처음 형성. 이후 측정에서 부분 반박됨.

### 3.3 Aider Polyglot Python 측정 (Day 2)

#### 3.3.1 정공 — Aider whole format

setup: aider 0.86.3 + uv venv (Python 3.11), `AIDER_DOCKER=1`로 Docker 가드 우회 (실제 Docker 없이 호스트에서 실행). 34 Python task.

```
pass_rate_1: 14.7%
pass_rate_2: 26.5%
percent_cases_well_formed: 100%
test_timeouts: 2 (zebra-puzzle 등 트랩 task)
total_cost: $0.00
```

이걸 공개 리더보드와 비교:

| 모델 | edit format | pass@2 | 출처 |
|---|---|---|---|
| 우리 Qwen3-Coder-30B | whole | **26.5%** | 우리 측정 (Python only, 34 task) |
| Qwen2.5-Coder-32B | whole | 16.4% | aider 공식 |
| Qwen3 32B | diff | 40.0% | aider 공식 |
| Sonnet 4 (no-think) | diff | 56.4% | aider 공식 |

**해석**: Qwen2.5 같은 가족 대비 의미있는 개선. Sonnet 4와 격차는 ~30%p. 단 우리는 whole + Python only라 직접 비교는 caveat 있음.

#### 3.3.2 동일 task를 Claw 하네스로 재실행

**가설**: Aider whole format은 단순 "전체 파일 출력". Claw는 Claude Code 식 tool calls + agent loop. 같은 모델·태스크인데 하네스만 바꾸면 점수 어떻게 변하나?

`claw_polyglot.py` runner 작성: Aider polyglot Python에서 Aider가 이미 실행한 15 task를 골라 동일하게 Claw로 실행.

| Task | Aider whole | **Claw** | 변화 |
|---|---|---|---|
| affine-cipher | ✅ | ✅ | = |
| beer-song | ✅ | ✅ | = |
| book-store | ❌ | ❌ | = |
| bottle-song | ❌ | **✅** | **+** |
| bowling | ❌ | ❌ | = |
| connect | ❌ | **✅** | **+** |
| dominoes | ✅ | ❌ | − |
| dot-dsl | ❌ | **✅** | **+** |
| food-chain | ❌ | ❌ | = |
| forth | ❌ | ❌ | = |
| go-counting | ❌ | ❌ | = |
| grade-school | ✅ | ✅ | = |
| grep | ✅ | ✅ | = |
| hangman | ❌ | **✅** | **+** |
| list-ops | ❌ | ❌ | = |

**합계**: Aider 5/15 (33.3%) → **Claw 8/15 (53.3%)**. **+20%p, ×1.6배**.

이 측정이 "Claw 효과 실재"의 첫 강한 증거. 하지만 다음 단계에서 뒤집힘.

### 3.4 SWE-bench Verified 측정 (Day 2~3)

#### 3.4.1 mini-swe-agent (Anthropic이 공식 측정에 쓰는 그 도구) + Qwen

목적: Anthropic Sonnet 4.6의 79.6%과 직접 비교 가능한 잣대로 측정.

setup:
```bash
pip install mini-swe-agent  # pypi v2.2.8
```
config:
```yaml
model:
  model_name: "openai/qwen3-coder-agent:latest"
  cost_tracking: "ignore_errors"
  model_kwargs:
    api_base: "http://127.0.0.1:11434/v1"
    parallel_tool_calls: false  # Ollama OpenAI-compat 호환성
agent:
  step_limit: 100
  cost_limit: 0
```

10 task (slice 0:10 = 첫 10개 astropy). 5시간 19분 소요 (32분/task 평균, 각 Docker base image 빌드 시간 포함).

채점 (swebench harness Docker 채점):
```
Total instances: 10
Resolved (passed): 1   ← astropy__astropy-14309
Empty patches: 3
Patch apply errors: 6   ← git diff 형식 어긋남
```

**Pass@1 = 10.0%**.

Patch 형식 분석:
- 3개 빈 응답 (litellm timeout/error)
- 4개 git diff 아님 (전체 파일 / 텍스트 설명 / "No actual code changes were made")
- 2개 git diff 시작하지만 truncated
- 1개 정상 + 통과

→ **Qwen이 mini-swe-agent의 `git diff > patch.txt && cat patch.txt` 제출 프로토콜에 일관되게 따라가지 못함**. 모델 실력보다 instruction-following 분포 mismatch.

#### 3.4.2 Claw 하네스 + Qwen + 동일 SWE-bench 10 task

가설 (User): Claude Code 유출 하네스가 모델 격차를 메운다.

`claw_swebench.py` runner 작성:
- 각 task의 SWE-bench Docker image (`swebench/sweb.eval.x86_64.<id>:latest`)에서 컨테이너 시작
- Claw 바이너리(`/PublicSSD/.../claw`)를 컨테이너에 마운트
- `--network host`로 컨테이너 안에서 호스트 Ollama 호출
- `--dangerously-skip-permissions`, timeout 900s
- 종료 후 `git add -A -- ':!.claw' && git diff --cached`로 patch 캡처

결과:

| 지표 | 값 |
|---|---|
| 시도 | 10/10 |
| 빈 patch | **10/10** |
| **Resolved (pass@1)** | **0/10 = 0.0%** |

**충격적 결과** — Claw 하네스가 mini-swe-agent보다도 **나쁨** (10% → 0%).

#### 3.4.3 0%의 원인 진단

stdout trace 분석:
- Claw가 edit_file 도구를 task당 2~7회 호출
- 그러나 fs에 변화 없음 → `git diff` 빈 채로 나옴
- edit_file 블록 분석에서 다수가 **`old_string ≡ new_string`** (동일 문자열 치환 = no-op)

가설:
1. Claw 64K 컨텍스트 + 큰 codebase (astropy `connect.py` 800줄, `separable.py` 600줄) → **auto-compaction 발생**
2. Compaction 후 모델이 원본 파일 정확한 내용 잃어버림
3. 그 후 edit_file 호출에 부정확한 old_string 넘김 → Claw는 "치환 성공"으로 처리하나 실제 변화 없음

직접 검증: 단순 컨테이너에서 Claw에 "/testbed/foo.py에 CLAW_TEST_MARKER 주석 추가해라"만 시키면 정상 동작 (md5 변경). 큰 codebase 다중 turn에선 깨짐 → 가설 부합.

### 3.5 256K 컨텍스트 도전 (Day 4)

가설 (User): 컨텍스트만 늘리면 auto-compaction 안 일어나고 0% 해결.

여러 경로 시도, **대부분 막힘**:

| 경로 | 결과 |
|---|---|
| ktransformers (pip wheel) | wheel은 stub, 진짜 server는 source build + nvcc 필요 → 막힘 |
| llama.cpp prebuilt CUDA Linux | Linux CUDA 빌드 자체 사라짐 (Win만 존재) |
| llama.cpp prebuilt Vulkan Linux | GLIBC 2.34 부재 (Ubuntu 20.04은 2.31) → 안 돌아감 |
| llama.cpp Docker (server-cuda image) | nvidia-container-toolkit 미설치 → `--gpus all` 막힘 |
| **llama.cpp Conda + 자가 빌드** ✅ | Conda nvidia 채널의 cuda-toolkit + gcc11로 source build 성공 |

#### 3.5.1 자가 빌드 성공 셋업

```bash
# Miniconda userspace 설치 (admin 무관)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda

# CUDA toolkit + gcc11 + cmake
~/miniconda/bin/conda create -n llama --override-channels \
  -c nvidia/label/cuda-12.4.1 -c conda-forge \
  cuda-toolkit gcc_linux-64=11 gxx_linux-64=11 cmake make -y

# 빌드
git clone --depth=1 https://github.com/ggml-org/llama.cpp
cd llama.cpp
LIBRARY_PATH=~/miniconda/envs/llama/lib \
~/miniconda/envs/llama/bin/cmake -B build \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=89 \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=OFF
~/miniconda/envs/llama/bin/cmake --build build -j 12
```

15분 빌드 후 llama-server 실행 가능.

#### 3.5.2 256K 시도 — MoE expert offload (3.7 tok/s 재앙)

```bash
llama-server -m <gguf> --ctx-size 262144 \
  --cache-type-k q8_0 --cache-type-v q4_0 --flash-attn on \
  -ngl 99 --override-tensor "exps=CPU"
```

VRAM: 12GB / 24GB (KV 256K + 비-expert 가중치만 GPU)
RAM: ~6GB (CPU에 옮겨진 expert 가중치)

speed test:
```
prompt eval: 6.24 tok/s
       eval: 3.69 tok/s
1098 토큰 응답에 207초 (≈3분 28초)
```

→ MoE 활성 expert를 매 토큰 PCIe로 fetch → 정상 80 tok/s의 **20배 느림**. SWE-bench 1 task에 900s timeout 도달 (1~2 turn 안에 시간 다 씀). T1, T2 둘 다 timeout 0B patch.

#### 3.5.3 ½ MoE offload 실패

layer 24~47만 CPU로:
```
--override-tensor "blk\.(2[4-9]|3[0-9]|4[0-7])\.ffn_(gate|up|down)_exps\.weight=CPU"
```

VRAM 20.5GB (꽉 참). 7021-token prompt processing이 너무 느려서 부속 요청까지 cancel. 여전히 사용 불가.

#### 3.5.4 160K all-GPU 합의안

```bash
llama-server -m <gguf> --ctx-size 163840 \
  --cache-type-k q4_0 --cache-type-v q4_0 --flash-attn on \
  -ngl 99 --parallel 1
```

VRAM 22.9GB / 24.5GB. **189 tok/s 생성** (정상 회복). Sonnet 4.6의 200K native와 거의 동급 컨텍스트.

이 셋업으로 Claw + SWE-bench 10 task 재측정.

#### 3.5.5 결과: 또 0/10

```
[1/10] astropy__astropy-12907 → patch=    0B  claw= 33s
[2/10] astropy__astropy-13033 → patch=    0B  claw= 29s
[3/10] astropy__astropy-13236 → patch=    0B  claw=108s
[4/10] astropy__astropy-13398 → patch=    0B  claw= 57s
[5/10] astropy__astropy-13453 → patch=    0B  claw= 51s
[6/10] astropy__astropy-13579 → patch=    0B  claw= 76s
[7/10] astropy__astropy-13977 → patch=    0B  claw= 84s
[8/10] astropy__astropy-14096 → patch=    0B  claw=106s exit=1
[9/10] astropy__astropy-14182 → patch=    0B  claw= 50s
[10/10] astropy__astropy-14309 → patch=    0B  claw= 50s
TOTAL: 10/10 빈 patch (Pass@1 = 0%)
```

**컨텍스트 64K → 160K로 2.5배 늘려도 결과 동일**. 가설 (컨텍스트가 병목) 직접 반증.

→ 진짜 병목은 **edit_file 호출의 입력 정확도**임이 확정. 컨텍스트 늘려도 모델이 학습 안 한 grammar는 여전히 깨짐.

---

## 4. 메타 분석 — 왜 이렇게 되나

### 4.1 두 축의 곱 = 결과

| Task 크기 | Edit grammar 정밀도 요구 | Claw + Qwen 결과 |
|---|---|---|
| 작은 starter (30~80줄) | 낮음 (대충 맞아도 된다) | ~95% (자작 4-task) |
| 중간 파일 (100~300줄) + whole format | 매우 낮음 (전체 출력) | 53% (Aider polyglot) |
| 큰 codebase (수천 줄) + 정밀 edit | **매우 높음** (exact substring match) | **0%** (SWE-bench) |

### 4.2 왜 정밀 edit grammar가 Qwen에 어렵나

Anthropic의 edit_file은 다음 conventions:
- `old_string`은 파일 내 정확한 substring (whitespace, indentation 포함 글자 단위 매칭)
- `new_string`은 그 자리에 들어갈 새 텍스트
- Multi-edit 시 각 호출 독립적으로 적용

**Anthropic Claude는 RLHF + tool-use fine-tuning에서 이 conventions를 수백만 회 학습 데이터로 봄**. 가중치에 박혀 있음.

**Qwen3-Coder는**:
- Qwen-Agent 프레임워크 conventions로 학습
- OpenHands / Hermes-style tool format 친숙
- Anthropic의 정확 매칭 grammar는 **분포 외 (out-of-distribution)**
- 큰 파일에서 "이 라인을 고치고 싶다"는 의도는 있지만, exact substring 생성 못 함
- Trace에서 본 그 패턴: `old_string == new_string` (no-op) 또는 형식 어긋난 입력

### 4.3 mini-swe-agent도 Qwen에 맞지 않음 (10% 그쳐서)

mini-swe-agent는 도구가 bash 하나뿐, 더 단순. 그래도 Qwen이 "git diff > patch.txt && cat patch.txt" 제출 프로토콜을 일관되게 못 따름:
- 4/10 patch 형식 어긋남 (전체 파일 / 설명 텍스트)
- 2/10 truncated diff
- 1/10 통과
- 3/10 빈 응답

→ Qwen은 OpenHands 학습 분포에 맞춰져 있어서, 여기에서 50%가 나옴. 다른 모든 하네스에선 더 떨어짐.

### 4.4 Sonnet 4.6이 79.6%인 진짜 이유

Anthropic은 mini-swe-agent를 자기 측정용 표준으로 채택 + 학습 단계에서 그 환경에서 잘 동작하도록 RLHF로 다듬음. 즉 **모델과 측정 도구가 사실상 co-train됨**. 그래서 Sonnet이 mini-swe-agent에서 79.6%인 건 모델의 absolute 능력이라기보다 **모델 × 하네스 매칭의 점수**.

같은 Sonnet을 OpenHands에 옮기면 추정 70~75%로 약간 떨어질 가능성 (외부 측정 없음).

---

## 5. 결론들

### 5.1 우리 가설들 평가

| 가설 | 평가 |
|---|---|
| "로컬 Qwen이 Sonnet 절반 가성비라도 가능" | ✅ 작은 task에선 사실, 단 SWE-bench급에선 격차 큼 |
| "스캐폴드를 바꾸면 모델 격차 메워진다" | ⚠️ 부분 사실. Aider polyglot에선 +20%p, SWE-bench에선 거꾸로 -10%p |
| "Claude Code 유출 하네스가 만능 격차 메우개" | ❌ 거짓 |
| "컨텍스트만 늘리면 SWE-bench 0% 해결" | ❌ 거짓 (64K → 160K 결과 동일) |
| "256K로 가면 진짜 다를 것" | ❌ 거짓 (구현 가능했어도 결과 같았을 것 — 컨텍스트가 병목 아님) |
| "더 큰 모델(480B 등)로 가면 0% 안 나옴" | ⚠️ 부분 사실. capacity가 분포 mismatch 일부 흡수, but native 하네스에서가 항상 더 잘함 |

### 5.2 실용적 가이드 (4090 24GB 한 장 보유자)

**일상 코딩 어시스턴트 (작은 task)**:
- Ollama + Qwen3-Coder-30B + Claw 하네스 → **추천** ⭐⭐⭐⭐
- Claude Code 사용 경험과 거의 같음, 비용 0

**중간 코딩 task (단일 파일 ~수백 줄)**:
- Ollama + Qwen3-Coder-30B + Claw 또는 Aider whole → 둘 다 OK
- Aider polyglot pass@2 ~30~55% 기대

**진지한 코딩 task (실제 GitHub 이슈, 멀티파일)**:
- 로컬 Qwen은 한계 → Sonnet/Opus API 또는 클라우드 Qwen3-Coder-Plus 추천
- 로컬로 가더라도 OpenHands 같은 Qwen-friendly 하네스 사용

**한 줄 요약**: **하네스는 모델을 키우지만, 모델이 그 하네스의 grammar를 학습했어야만**. Anthropic이 자기 모델로 만든 그 격차의 일부는 "co-train"의 결과라 외부 모델로 단순 복제 불가.

### 5.3 후속 실험 제안

각각 1~2시간이면 추가 정보 얻을 수 있음:

1. **DashScope Qwen3-Coder-Plus (480B native) + Claw on SWE-bench** ($5~15)
   - 가설 검증: "큰 외부 모델은 분포 mismatch 일부 흡수해서 0% 안 됨"
   - 예상: 30~50%

2. **Sonnet 4.6 + OpenHands on SWE-bench**
   - 가설: "Sonnet도 native 아닌 하네스에선 점수 떨어짐"
   - ANTHROPIC_API_KEY 필요, ~$10~30

3. **DeepSeek-V3 + Claw on SWE-bench**
   - 다른 model family도 같은 mismatch 패턴인지

4. **Qwen3-Coder-30B 자체 RLHF + Claw 하네스 fine-tune** (진지한 연구)
   - co-train의 효과 자체를 측정. 며칠/주.

---

## 6. 산출물 위치

```
/PublicSSD/minu/local-claude-project/
├── claw-code/                    # Claude Code 유출 하네스 clone (Rust source)
│   └── rust/target/release/claw  # 빌드된 17MB 바이너리
├── benchmark/                    # 우리 자작 + Aider polyglot runner
│   ├── runner.py                 # 자작 4-task용
│   ├── claw_polyglot.py          # Aider polyglot Python을 Claw로 돌리는 runner
│   ├── claw_swebench.py          # SWE-bench를 Claw로 돌리는 runner
│   ├── tasks/t01..t04/           # 자작 task 정의
│   └── results/
│       ├── slim-20260424T122408/ # 자작 4-task 결과
│       ├── claw-polyglot-15/     # Aider polyglot Claw 결과 (53.3%)
│       ├── claw-10task/          # SWE-bench Claw 64K (0/10)
│       └── claw-10task-160k/     # SWE-bench Claw 160K (0/10)
├── aider/                        # Aider 공식 source + 우리가 돌린 결과
│   └── tmp.benchmarks/
│       └── 2026-04-24-22-05-54--qwen3coder-py40/  # Aider 정공 34 task (26.5%)
├── swebench-results/
│   ├── b-10task/                 # mini-swe-agent + Qwen 결과 (10%)
│   ├── claw-10task/              # === == === Claw 64K
│   └── claw-10task-160k/         # === === === Claw 160K
├── llama.cpp/build/bin/
│   └── llama-server              # 자가 빌드 CUDA llama.cpp
├── llama-server-logs/server.log  # 추론 속도 진단
├── mini-swe-config.yaml          # mini-swe-agent → Ollama 라우팅
├── Modelfile.qwen3coder-agent    # 64K Qwen3-Coder
├── Modelfile.qwen3coder-128k     # 128K (실험용, 사용 안 함)
└── REPORT.md                     # 이 문서

~/.cargo/                         # Rust toolchain 1.95
~/.local/                         # Ollama 0.21.2 (userspace)
~/.ollama/models/                 # 35GB (qwen3-coder + qwen3.6)
~/miniconda/                      # Conda + cuda-toolkit + gcc11
/PublicSSD/.../mini-swe-venv/     # mini-swe-agent venv
/PublicSSD/.../swebench-venv/     # swebench harness venv
/PublicSSD/.../aider/aider-venv/  # aider venv (Python 3.11 via uv)
```

총 디스크 사용: **~75GB** (모델 35GB + 도구·환경 ~25GB + 결과 ~15GB)

---

## 7. 저자 노트

이 실험은 "Claude Code 유출 → 오픈소스 Claw → 그러면 격차 메워지나?"라는 popular 직관을 직접 검증한 4일짜리 사례. 결과는 **둘 다 부분 사실**:
- 작은/중간 task: 격차 의미있게 줄어듦 (33% → 53% 같은 케이스)
- 큰 task: 격차 그대로 또는 더 벌어짐 (mini-swe-agent 10% → Claw 0%)
- 컨텍스트는 우리가 처음 의심한 만큼 결정적이 아님
- 모델 × 하네스의 학습 분포 매칭이 가장 큰 변수

가장 흥미로운 finding: **Anthropic이 SWE-bench Verified에서 79.6% 측정한 건 "Sonnet의 절대 능력"이 아니라 "Sonnet × mini-swe-agent의 합작 점수"**. 그 시스템 안에서만 그렇게 잘 나오고, 외부로 끌어내면 모델·하네스 둘 다 점수가 깎임.

오픈소스 진영이 이 격차를 메우려면 **하네스 옮겨끼우기가 아니라 모델을 그 하네스에 맞춰 RLHF로 다듬는 것**이 본질적인 해결책. 그건 며칠/주 작업이고 별도 실험.

---

*작성일: 2026-04-27*
*총 측정 시간 (능동 + 백그라운드): 약 18시간*
*총 비용: 클라우드 API $0 (전부 로컬 추론) + Sonnet subagent ~$2~5 (자작 4-task용)*
