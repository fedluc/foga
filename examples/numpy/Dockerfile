FROM python:3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ARG NUMPY_REPO=https://github.com/numpy/numpy.git
ARG NUMPY_REF=v2.4.4

ENV PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY examples/numpy/foga.yml /tmp/foga.yml

RUN python3 -m pip install --no-cache-dir foga

WORKDIR /workspaces

RUN git clone --depth 1 "${NUMPY_REPO}" numpy \
    && cd numpy \
    && git fetch --depth 1 origin "${NUMPY_REF}" \
    && git checkout --detach FETCH_HEAD \
    && cp /tmp/foga.yml /workspaces/numpy/foga.yml

WORKDIR /workspaces/numpy

RUN foga install --target system \
    && foga install --target build-env
