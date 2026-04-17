# 01-python-only

This is the smallest runnable `foga` example in the repository.

It shows:

- a pure Python package with `numpy` and `rich`
- a `uv`-based development install
- a `python-build` package build
- a `pytest` runner

Files:

- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`src/vector_demo`](src/vector_demo)
- [`tests/test_vector_demo.py`](tests/test_vector_demo.py)
- [`run-foga`](run-foga)

Typical usage:

```bash
./run-foga
./run-foga inspect
./run-foga build
```
