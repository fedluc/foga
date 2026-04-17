#!/usr/bin/env bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# Install the development toolchain that `foga` users commonly need
# when building and testing Python packages with C/C++ bindings.
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    build-essential \
    bubblewrap \
    clang \
    cmake \
    curl \
    gdb \
    git \
    gh \
    ninja-build \
    pkg-config
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

# Install uv so the development container matches the repository workflow.
curl -LsSf https://astral.sh/uv/install.sh | sh
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" || \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
export PATH="$HOME/.local/bin:$PATH"

# Sync this repository together with the development and docs extras used to
# build, test, and document `foga` itself.
uv sync --extra dev --extra docs

# Install Codex in the container so the development environment matches the
# local workflow expected for this repository.
npm install -g @openai/codex
