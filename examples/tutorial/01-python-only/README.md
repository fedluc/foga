# 01-python-only

This is the smallest runnable `foga` example in the repository.

It shows:

- a pure Python package with `numpy` and `rich`
- a `uv`-based development install
- a `python-build` package build
- a dedicated Docker environment so the example does not touch the host machine
- a self-contained `uv` project that installs `foga` from PyPI

Files:

- [`Dockerfile`](Dockerfile)
- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`src/vector_demo`](src/vector_demo)
- [`run_example.py`](run_example.py)

Typical usage from the repository root:

```bash
python run-example.py python-only
python run-example.py python-only --list-steps
python run-example.py --mode host python-only build
```

The default launcher path builds the example Docker image and runs the
`run_example.py` walkthrough in the container. `--mode host` is available only
when you intentionally want a local run.
