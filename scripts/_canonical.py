"""Shared canonical-data loader for the Python build scripts.

Both ``build_chart_figures.py`` and ``build_precomputed.py`` need the same
archetype/cluster palette as the Astro shell at ``site/src/lib/canonical.ts``.
This module reads ``data/canonical.json`` once and exposes the derived dicts
so the palette only lives in one place. A test in ``site/tests/canonical.test.mjs``
asserts no inline duplicates in the Python files.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CANONICAL = json.loads((ROOT / "data" / "canonical.json").read_text())

ARCHETYPE_COLORS: dict[str, str] = {a["name"]: a["color"] for a in CANONICAL["archetypes"]}

TOPIC_MAPPING: dict[str, dict[str, str]] = {
    c["name"]: {"color": c["color"]} for c in CANONICAL["clusters"]
}
