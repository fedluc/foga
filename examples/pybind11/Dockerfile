FROM mcr.microsoft.com/devcontainers/cpp:1-ubuntu-24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PYBIND11_REF=288913638bb2da563f1c39e7d07071c2f21bfb25

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        clang-format \
        clang-tidy \
        cmake \
        gawk \
        git \
        ninja-build \
        python3-dev \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        build \
        foga==0.1.0 \
        nox \
        pre-commit \
        uv

WORKDIR /workspaces

RUN git clone https://github.com/pybind/pybind11.git \
    && cd pybind11 \
    && git checkout "${PYBIND11_REF}" \
    && uv venv .venv \
    && uv pip install -p .venv/bin/python -r tests/requirements.txt

COPY examples/pybind11/foga.yml /workspaces/pybind11/foga.yml

WORKDIR /workspaces/pybind11
