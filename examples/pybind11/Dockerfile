FROM python:3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ARG PYBIND11_REPO=https://github.com/pybind/pybind11.git
ARG PYBIND11_REF=288913638bb2da563f1c39e7d07071c2f21bfb25

ENV PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY examples/pybind11/foga.yml /tmp/foga.yml

RUN python3 -m pip install --no-cache-dir foga

WORKDIR /workspaces

RUN git clone --depth 1 "${PYBIND11_REPO}" pybind11 \
    && cd pybind11 \
    && git fetch --depth 1 origin "${PYBIND11_REF}" \
    && git checkout "${PYBIND11_REF}" \
    && cp /tmp/foga.yml /workspaces/pybind11/foga.yml

WORKDIR /workspaces/pybind11

RUN foga install --target system
RUN foga install --target python-deps
