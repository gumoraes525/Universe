"""Shard persistence for generated pipeline outputs."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from universe_gen.validation.validator import validate_schema


class ShardStore:
    """Store stage output shards under output/{run_id}/{stage}/{entity_id}.json."""

    def __init__(self, root: Path = Path("output")) -> None:
        self.root = root

    def shard_path(self, run_id: str, stage: str, entity_id: str) -> Path:
        """Return the shard path for an entity."""
        safe_id = entity_id.replace(".", "_")
        return self.root / run_id / stage / f"{safe_id}.json"

    def write(
        self, run_id: str, stage: str, entity_id: str, payload: Mapping[str, Any], schema: str
    ) -> Path:
        """Validate and write a shard."""
        result = validate_schema(payload, schema)
        if not result.success:
            msg = "; ".join(issue.message for issue in result.issues)
            raise ValueError(msg)
        path = self.shard_path(run_id, stage, entity_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def read(self, run_id: str, stage: str, entity_id: str) -> dict[str, Any]:
        """Read a shard."""
        return dict(
            json.loads(self.shard_path(run_id, stage, entity_id).read_text(encoding="utf-8"))
        )

    def index(self, run_id: str) -> dict[str, Path]:
        """Build an index by hierarchical ID."""
        index: dict[str, Path] = {}
        for path in (self.root / run_id).glob("*/*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            entity_id = data.get("id")
            if isinstance(entity_id, str):
                index[entity_id] = path
        return index
