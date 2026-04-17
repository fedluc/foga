FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive UV_LINK_MODE=copy

WORKDIR /workspace/foga

RUN python -m pip install --no-cache-dir uv

COPY . /workspace/foga

RUN uv sync --frozen --extra dev
RUN uv run foga --config examples/tutorial/03-pybind11-tests/foga.yml install --target system

ENTRYPOINT ["python", "run-example.py", "--mode", "host", "pybind11-tests"]
