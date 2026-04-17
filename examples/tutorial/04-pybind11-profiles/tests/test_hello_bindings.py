from __future__ import annotations

from hello_bindings import greet


def test_greet_returns_expected_message() -> None:
    assert greet("foga") == "hello, foga!"
