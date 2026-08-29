"""Storage for the annotation tool.

DESIGN SPLIT (deliberate):
  * LOADERS are DONE, so the app runs on first launch against the synthetic seeds.
  * SAVERS + the per-category COUNT logic are TODO STUBS to finish.

Follow the same atomic-write pattern used elsewhere (temp file + os.replace).
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .schema import Annotation, Taxonomy, Trace

HERE = Path(__file__).resolve().parent
SEEDS_DIR = HERE / "seeds"
SEED_TRACES = SEEDS_DIR / "traces.json"
SEED_TAXONOMY = SEEDS_DIR / "taxonomy.json"

# Annotations + any grown taxonomy get written here (gitignored via state/).
STATE_DIR = HERE.parent / "state"
ANNOTATIONS_FILE = STATE_DIR / "annotations.json"
TAXONOMY_FILE = STATE_DIR / "taxonomy.json"


# --------------------------------------------------------------------------- #
# LOADERS \u2014 DONE. These make the app run on first launch. Do not gut them.
# --------------------------------------------------------------------------- #
def load_traces(path: Path = SEED_TRACES) -> List[Trace]:
    """Load traces from a JSON file. Data-agnostic: any dict with an 'id' works.

    Accepts either a top-level list of trace dicts, or {"traces": [...]}.
    """
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data["traces"] if isinstance(data, dict) else data
    return [Trace.from_dict(d) for d in items]


def load_taxonomy() -> Taxonomy:
    """Load the working taxonomy: prefer the grown copy in state/, else the seed."""
    src = TAXONOMY_FILE if TAXONOMY_FILE.exists() else SEED_TAXONOMY
    with src.open("r", encoding="utf-8") as fh:
        return Taxonomy.from_dict(json.load(fh))


def load_annotations() -> Dict[str, Annotation]:
    """Load saved annotations keyed by trace_id. Empty dict on first launch."""
    if not ANNOTATIONS_FILE.exists():
        return {}
    with ANNOTATIONS_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {a["trace_id"]: Annotation.from_dict(a) for a in data.get("annotations", [])}


def _atomic_write_json(path: Path, payload: Any) -> None:
    """Reference atomic write \u2014 reuse this in the TODO savers below."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------------------------------- #
# SAVERS + COUNTS \u2014 TODO STUBS. This is YOUR exercise.
# Finish these with your AI coding assistant, one per Git feature branch.
# --------------------------------------------------------------------------- #
def save_annotations(annotations: Dict[str, Annotation]) -> None:
    """Persist annotations atomically to ANNOTATIONS_FILE (state/, gitignored)."""
    payload = {"annotations": [a.to_dict() for a in annotations.values()]}
    _atomic_write_json(ANNOTATIONS_FILE, payload)


def save_taxonomy(taxonomy: Taxonomy) -> None:
    """TODO(you): persist the grown taxonomy atomically to TAXONOMY_FILE.

    Hint: _atomic_write_json(TAXONOMY_FILE, taxonomy.to_dict()).
    """
    raise NotImplementedError("save_taxonomy is a TODO \u2014 see the TODO notes .")


def category_counts(annotations: Dict[str, Annotation], taxonomy: Taxonomy) -> Dict[str, int]:
    """TODO(you): the OUTPUT OF AXIAL CODING \u2014 how many failures per category.

    Return {category_name: count} covering EVERY taxonomy category (0 if unused),
    counting each tag occurrence across all annotations. This is the number you
    report as your failure taxonomy.
    """
    raise NotImplementedError("category_counts is a TODO \u2014 see the TODO notes .")


def export_review(annotations: Dict[str, Annotation], taxonomy: Taxonomy) -> str:
    """TODO(you): export the coded taxonomy + counts as a string (JSON or Markdown).

    Purpose: so you can SHOW a failure taxonomy.
    """
    raise NotImplementedError("export_review is a TODO \u2014 see the TODO notes .")
