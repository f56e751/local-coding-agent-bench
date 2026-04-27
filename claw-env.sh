#!/usr/bin/env bash
# Source this before running claw: `source /PublicSSD/minu/local-claude-project/claw-env.sh`

export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama-local"
# ANTHROPIC_MODEL is only consulted by claw in REPL mode, so it helps the
# interactive `claw` invocation but is ignored by `claw prompt`. The wrapper
# below injects --model for both cases.
export ANTHROPIC_MODEL="openai/qwen3-coder-agent:latest"
unset  ANTHROPIC_API_KEY
unset  ANTHROPIC_BASE_URL

# Claw binary on PATH
export PATH="/PublicSSD/minu/local-claude-project/claw-code/rust/target/release:$PATH"

# Wrapper that injects --model unless user already provided one.
# Usage: `claw "prompt"` or `claw --model other/foo prompt "..."`
claw() {
    local bin="/PublicSSD/minu/local-claude-project/claw-code/rust/target/release/claw"
    local has_model=false
    for a in "$@"; do
        case "$a" in
            --model|--model=*) has_model=true; break ;;
        esac
    done
    if $has_model; then
        "$bin" "$@"
    else
        "$bin" --model "openai/qwen3-coder-agent:latest" "$@"
    fi
}

echo "claw env loaded (Ollama @ $OPENAI_BASE_URL, default model: openai/qwen3-coder-agent:latest)"
