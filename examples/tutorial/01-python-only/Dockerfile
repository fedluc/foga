FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive UV_LINK_MODE=copy

WORKDIR /workspace/example

RUN python -m pip install --no-cache-dir uv

COPY . /workspace/example

RUN uv sync --extra dev

ENTRYPOINT ["uv", "run", "foga", "--config", "foga.yml"]
