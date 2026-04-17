from __future__ import annotations

import numpy as np


def centered_norm(values: list[float]) -> float:
    data = np.asarray(values, dtype=float)
    centered = data - data.mean()
    return float(np.linalg.norm(centered))
