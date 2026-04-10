#!/usr/bin/env bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# Install the native development toolchain that `devkit` users commonly need
# when building and testing Python packages with C/C++ bindings.
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    cmake \
    gdb \
    git \
    gh \
    ninja-build \
    pkg-config
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

# Upgrade pip first so editable installs and modern packaging tools behave
# consistently inside the fresh container image.
python3 -m pip install --upgrade pip

# Install this repository in editable mode together with the development
# dependencies used to build, test, and publish `devkit` itself.
python3 -m pip install -e ".[dev]"

# Install Codex in the container so the development environment matches the
# local workflow expected for this repository.
npm install -g @openai/codex
