"""Review checkpoint serialization."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from universe_gen.validation.validator import validate_schema


@dataclass(frozen=True)
class Selection:
    """Reviewer selection for an individual item."""

    id: str
    selected: bool
    rationale: str
    reviewer: str | None = None

    def to_json(self) -> dict[str, Any]:
        """Serialize selection."""
        data: dict[str, Any] = {
            "id": self.id,
            "selected": self.selected,
            "rationale": self.rationale,
        }
        if self.reviewer is not None:
            data["reviewer"] = self.reviewer
        return data


@dataclass(frozen=True)
class Checkpoint:
    """Review checkpoint with deterministic regeneration provenance."""

    checkpoint_id: str
    stage: str
    generated_set: list[str]
    provenance: dict[str, Any]
    shortlist: list[Selection] = field(default_factory=list)
    reviewer_notes: str = ""
    accepted: bool = False

    def to_json(self) -> dict[str, Any]:
        """Serialize to canonical review schema format."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "stage": self.stage,
            "generated_set": self.generated_set,
            "shortlist": [selection.to_json() for selection in self.shortlist],
            "reviewer_notes": self.reviewer_notes,
            "accepted": self.accepted,
            "provenance": self.provenance,
        }

    def validate(self) -> None:
        """Raise when checkpoint JSON does not match the review schema."""
        result = validate_schema(self.to_json(), "review/checkpoint.schema.json")
        if not result.success:
            msg = "; ".join(issue.message for issue in result.issues)
            raise ValueError(msg)

    def save(self, directory: Path) -> Path:
        """Write checkpoint using the project naming convention."""
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / self.filename()
        self.validate()
        path.write_text(
            json.dumps(self.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return path

    def filename(self) -> str:
        """Return checkpoint file name including stage and provenance identifier."""
        return f"checkpoint_{self.stage}_{self.checkpoint_id}.json"

    @classmethod
    def load(cls, path: Path) -> Checkpoint:
        """Load a checkpoint for pipeline resumption."""
        data = json.loads(path.read_text(encoding="utf-8"))
        selections = [Selection(**item) for item in data.get("shortlist", [])]
        return cls(
            checkpoint_id=str(data["checkpoint_id"]),
            stage=str(data["stage"]),
            generated_set=[str(item) for item in data["generated_set"]],
            provenance=dict(data["provenance"]),
            shortlist=selections,
            reviewer_notes=str(data.get("reviewer_notes", "")),
            accepted=bool(data.get("accepted", False)),
        )
