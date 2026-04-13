from __future__ import annotations

project = "foga"
copyright = "2026, Federico Lucco Castello"
author = "Federico Lucco Castello"

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "foga"
html_static_path = ["_static"]

myst_enable_extensions = [
    "colon_fence",
]
