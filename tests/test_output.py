"""Tests for shared CLI output styling."""

from foga.output import STYLES


def test_warning_and_error_colors_use_distinct_semantic_accents() -> None:
    """Warnings should use amber while errors keep the brand pink."""
    assert STYLES["warning"] == "\033[1;38;2;245;158;11m"
    assert STYLES["error"] == "\033[1;38;2;255;76;165m"
