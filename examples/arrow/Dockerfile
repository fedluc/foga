FROM python:3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ARG ARROW_REPO=https://github.com/apache/arrow.git
ARG ARROW_REF=36c8c9a24aec70fb41441c6a1a2a28b777d351e3

ENV PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY examples/arrow/foga.yml /tmp/foga.yml

RUN python3 -m pip install --no-cache-dir foga

WORKDIR /workspaces

RUN git clone --depth 1 "${ARROW_REPO}" arrow \
    && cd arrow \
    && git fetch --depth 1 origin "${ARROW_REF}" \
    && git checkout "${ARROW_REF}" \
    && cp /tmp/foga.yml /workspaces/arrow/foga.yml

WORKDIR /workspaces/arrow

RUN foga install --target system \
    && foga install --target build-env

CMD ["bash"]
