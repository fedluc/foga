FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive UV_LINK_MODE=copy

WORKDIR /workspace/foga

RUN python -m pip install --no-cache-dir uv

COPY . /workspace/foga

RUN uv sync --frozen --extra dev

ENTRYPOINT ["python", "run-example.py", "--mode", "host", "python-only"]
