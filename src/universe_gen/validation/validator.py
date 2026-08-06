"""JSON Schema validation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from universe_gen.validation.plausibility import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)

SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"


def _schema_resources() -> Registry:
    registry = Registry()
    for path in SCHEMA_ROOT.rglob("*.schema.json"):
        contents = load_schema(path.relative_to(SCHEMA_ROOT).as_posix())
        uri = path.resolve().as_uri()
        registry = registry.with_resource(uri, Resource.from_contents(contents))
        schema_id = contents.get("$id")
        if isinstance(schema_id, str):
            registry = registry.with_resource(schema_id, Resource.from_contents(contents))
    return registry


def load_schema(relative_path: str) -> dict[str, Any]:
    """Load a schema by path relative to the repository schema root."""
    import json

    with (SCHEMA_ROOT / relative_path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    return dict(data)


def validate_schema(payload: Mapping[str, Any], schema_path: str) -> ValidationResult:
    """Validate a payload against a repository JSON Schema."""
    schema_file = SCHEMA_ROOT / schema_path
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema, registry=_schema_resources())
    issues = [
        ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="schema_validation_failed",
            message=error.message,
            path="/".join(str(part) for part in error.absolute_path),
            repair_suggestion=f"Conform payload to {schema_file.name}.",
        )
        for error in sorted(validator.iter_errors(payload), key=lambda item: item.path)
    ]
    return ValidationResult.from_issues(issues)
