"""Stable hierarchical dot-notation identifiers."""

from __future__ import annotations

import re
from dataclasses import dataclass

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
_SEGMENT_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, order=True)
class HierarchicalID:
    """Hierarchical identifier represented as dot-separated path segments."""

    parts: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.parts or any(_SEGMENT_RE.fullmatch(part) is None for part in self.parts):
            msg = f"Invalid hierarchical ID parts: {self.parts!r}"
            raise ValueError(msg)

    def __str__(self) -> str:
        return ".".join(self.parts)

    @classmethod
    def parse(cls, value: str) -> HierarchicalID:
        """Parse and validate a dot-notation identifier."""
        if _ID_RE.fullmatch(value) is None:
            msg = f"Invalid hierarchical ID: {value!r}"
            raise ValueError(msg)
        return cls(tuple(value.split(".")))

    @classmethod
    def root(cls, name: str = "universe") -> HierarchicalID:
        """Create a root identifier."""
        return cls.parse(name)

    def child(self, local_identifier: str) -> HierarchicalID:
        """Derive a stable child ID from this ID and a local segment."""
        if _SEGMENT_RE.fullmatch(local_identifier) is None:
            msg = f"Invalid local identifier: {local_identifier!r}"
            raise ValueError(msg)
        return HierarchicalID((*self.parts, local_identifier))

    @staticmethod
    def is_valid(value: str) -> bool:
        """Return whether a string matches the identifier schema pattern."""
        return _ID_RE.fullmatch(value) is not None
