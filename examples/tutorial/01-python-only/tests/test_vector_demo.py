from __future__ import annotations

import math

from vector_demo import centered_norm


def test_centered_norm_matches_expected_value() -> None:
    assert centered_norm([1.0, 2.0, 3.0]) == math.sqrt(2.0)
