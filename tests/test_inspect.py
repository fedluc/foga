"""Tests for inspect output rendering details."""

from __future__ import annotations

from devkit.cli import inspect as inspect_module


def test_emit_document_colorizes_tty_output(monkeypatch, capsys) -> None:
    """Inspect output adds ANSI colors when writing to an interactive terminal."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(inspect_module.sys.stdout, "isatty", lambda: True)

    inspect_module._emit_document(  # noqa: SLF001 - intentional module-level unit test
        {
            "summary": {
                "command": "build",
                "selection": "native",
                "targets": ["native_tests"],
            }
        }
    )

    captured = capsys.readouterr()
    assert "\033[" in captured.out
    assert "summary" in captured.out
    assert "native_tests" in captured.out


def test_emit_document_keeps_plain_yaml_for_non_tty(monkeypatch, capsys) -> None:
    """Inspect output stays plain YAML when stdout is not a terminal."""
    monkeypatch.setattr(inspect_module.sys.stdout, "isatty", lambda: False)

    inspect_module._emit_document(  # noqa: SLF001 - intentional module-level unit test
        {
            "summary": {
                "command": "build",
                "selection": "native",
            }
        }
    )

    captured = capsys.readouterr()
    assert "\033[" not in captured.out
    assert captured.out == ("summary:\n  command: build\n  selection: native\n")
