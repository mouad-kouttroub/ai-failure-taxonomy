"""Schema for the annotation / trace-review tool.

DATA-AGNOSTIC BY DESIGN. A "trace" is the full record of one AI session. The tool
does not hard-code any domain: it reads whatever fields a trace JSON provides and
renders the known ones nicely, falling back to raw display for the rest. This lets
the synthetic seed set AND real traces you drop in later both work.

Minimal required field: `id`. Everything else is optional and rendered if present.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Canonical, recognized trace fields (rendered specially when present).
# Anything else in a trace dict is shown under "Other fields" verbatim.
KNOWN_TRACE_FIELDS = ("id", "prompt", "response", "tool_calls", "retrieval", "metadata")


@dataclass
class Trace:
    """One AI-output record. `raw` keeps every original field for round-tripping."""

    id: str
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Trace":
        if "id" not in d:
            raise ValueError("Every trace must have an 'id' field.")
        return cls(id=str(d["id"]), raw=dict(d))

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)

    def other_fields(self) -> Dict[str, Any]:
        return {k: v for k, v in self.raw.items() if k not in KNOWN_TRACE_FIELDS}


@dataclass
class Taxonomy:
    """An EDITABLE failure taxonomy. Categories grow as you axial-code (grounded theory).

    Stored as a flat list of category dicts: {"name": str, "description": str}.
    """

    categories: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Taxonomy":
        return cls(categories=list(d.get("categories", [])))

    def to_dict(self) -> Dict[str, Any]:
        return {"categories": self.categories}

    def names(self) -> List[str]:
        return [c["name"] for c in self.categories]

    def add(self, name: str, description: str = "") -> None:
        if name and name not in self.names():
            self.categories.append({"name": name, "description": description})


@dataclass
class Annotation:
    """The candidate's open-coding note + assigned taxonomy tags for one trace."""

    trace_id: str
    note: str = ""                       # open-coding: the FIRST failure observed
    tags: List[str] = field(default_factory=list)  # axial-coding: taxonomy categories

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Annotation":
        return cls(
            trace_id=str(d["trace_id"]),
            note=str(d.get("note", "")),
            tags=list(d.get("tags", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"trace_id": self.trace_id, "note": self.note, "tags": self.tags}
