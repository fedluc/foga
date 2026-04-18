FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace/example

RUN python -m pip install --no-cache-dir foga

COPY pyproject.toml foga.yml CMakeLists.txt /workspace/example/
COPY example-instructions.md /workspace/example/example-instructions.md
COPY src /workspace/example/src
COPY cpp /workspace/example/cpp

RUN printf '\nif [ -z "${FOGA_TUTORIAL_INSTRUCTIONS_SHOWN:-}" ]; then\n  export FOGA_TUTORIAL_INSTRUCTIONS_SHOWN=1\n  cat /workspace/example/example-instructions.md\nfi\n' >> /root/.bashrc
