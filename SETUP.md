# Reproducing the environment

The repo intentionally does **not** vendor large external dependencies (clones of Aider, Claw Code, llama.cpp, etc.) or Python virtualenvs — they're easy to recreate and add gigabytes of bulk. This file shows how to set up everything from scratch.

Tested target: **Ubuntu 20.04 / 22.04 + RTX 4090 (24GB)**. Other GPUs work with adjustments to context size.

---

## 1. Base toolchain (no sudo if possible)

```bash
# uv (Python multi-version manager + venv tool, used by everything below)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Rust toolchain (for building Claw Code)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal
source "$HOME/.cargo/env"

# Ollama userspace install
mkdir -p $HOME/.local
curl -fL -o /tmp/ollama.tar.zst https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tar.zst
zstd -d -c /tmp/ollama.tar.zst | tar -C $HOME/.local -xf -

# Docker (needs admin) — used for SWE-bench harness grading
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER   # log out/in or `newgrp docker` afterward
```

## 2. Pull Qwen3-Coder-30B-A3B + create context variants

```bash
ollama pull qwen3-coder:30b   # ~18GB

# Default 64K variant (the one used in most measurements)
ollama create qwen3-coder-agent -f Modelfile.qwen3coder-agent

# 128K variant (used for one ablation, results were equivalent)
ollama create qwen3-coder-128k -f Modelfile.qwen3coder-128k
```

Recommended Ollama runtime env:

```bash
export OLLAMA_KV_CACHE_TYPE="q8_0"
export OLLAMA_FLASH_ATTENTION="1"
nohup $HOME/.local/bin/ollama serve > $HOME/.ollama/logs/serve.log 2>&1 &
```

## 3. Clone & build Claw Code (Claude Code leaked harness re-implementation)

```bash
git clone https://github.com/instructkr/claw-code.git
cd claw-code/rust
cargo build --workspace --release   # ~1 minute on 16-core CPU
# binary lives at claw-code/rust/target/release/claw

source ../../claw-env.sh   # this repo's env wrapper
```

## 4. Aider (for Aider polyglot benchmark runs)

```bash
git clone https://github.com/Aider-AI/aider.git
cd aider
uv venv --python 3.11 aider-venv
source aider-venv/bin/activate
uv pip install -e .[dev]
mkdir -p tmp.benchmarks
git clone https://github.com/Aider-AI/polyglot-benchmark tmp.benchmarks/polyglot-benchmark
```

Sample run:
```bash
export OPENAI_API_BASE="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="dummy"
export AIDER_DOCKER=1   # bypass docker guard (we run on host instead)
python benchmark/benchmark.py qwen3coder-py40 \
  --new --model openai/qwen3-coder-agent:latest \
  --edit-format whole --tries 2 --threads 1 \
  --num-tests 40 --languages python \
  --exercises-dir polyglot-benchmark
```

## 5. mini-swe-agent (SWE-bench standard scaffold)

```bash
uv venv --python 3.11 mini-swe-venv
uv pip install --python mini-swe-venv/bin/python mini-swe-agent
```

Sample run:
```bash
export MSWEA_COST_TRACKING=ignore_errors
mini-swe-venv/bin/mini-extra swebench \
  --subset verified --split test --slice 0:10 \
  --workers 1 --output swebench-results/b-10task \
  -c mini-swe-venv/lib/python3.11/site-packages/minisweagent/config/benchmarks/swebench.yaml \
  -c mini-swe-config.yaml
```

## 6. SWE-bench harness (Docker grading)

```bash
uv venv --python 3.11 swebench-venv
uv pip install --python swebench-venv/bin/python swebench

# Grade a preds.json (first run pulls many GB of base images)
swebench-venv/bin/python -m swebench.harness.run_evaluation \
  --predictions_path swebench-results/b-10task/preds.json \
  --max_workers 2 --run_id qwen3coder-mini-10 \
  --dataset_name princeton-nlp/SWE-bench_Verified
```

## 7. (optional) llama.cpp self-build for 256K experiments

This only matters if you want to retry the 256K-context experiment from §3.5 of REPORT.md. **Result was negative** (3.7 tok/s with MoE expert offload, dropped to 0% pass on SWE-bench). Reproducing requires Conda for the CUDA toolkit since Ubuntu 20.04 lacks nvcc by default:

```bash
# Miniconda userspace
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda create -n llama --override-channels \
  -c nvidia/label/cuda-12.4.1 -c conda-forge \
  cuda-toolkit gcc_linux-64=11 gxx_linux-64=11 cmake make -y

# Build llama.cpp
git clone --depth=1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
ENV=$HOME/miniconda/envs/llama
LIBRARY_PATH=$ENV/lib \
  $ENV/bin/cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 \
  -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF
$ENV/bin/cmake --build build -j 12

# Run server with 160K (sweet spot for 4090)
LD_LIBRARY_PATH=$ENV/lib:./build/bin \
./build/bin/llama-server \
  -m $HOME/.ollama/models/blobs/sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a \
  --host 127.0.0.1 --port 8080 --ctx-size 163840 \
  --cache-type-k q4_0 --cache-type-v q4_0 --flash-attn on \
  -ngl 99 --parallel 1 --threads 12 --jinja
```
