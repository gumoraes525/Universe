"""Configurable physical plausibility checks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ValidationSeverity(StrEnum):
    """Validation severities used by the rejection handler."""

    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass(frozen=True)
class ValidationIssue:
    """Single validation issue."""

    severity: ValidationSeverity
    code: str
    message: str
    path: str = ""
    repair_suggestion: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Validation outcome with error details and repair suggestions."""

    success: bool
    issues: tuple[ValidationIssue, ...] = ()
    repaired_payload: Mapping[str, Any] | None = None

    @property
    def repair_suggestions(self) -> tuple[str, ...]:
        """Return non-empty repair suggestions from issues."""
        return tuple(issue.repair_suggestion for issue in self.issues if issue.repair_suggestion)

    @classmethod
    def ok(cls) -> ValidationResult:
        """Create a successful result."""
        return cls(True)

    @classmethod
    def from_issues(cls, issues: list[ValidationIssue]) -> ValidationResult:
        """Create a result from issues."""
        blocking = any(issue.severity is not ValidationSeverity.WARNING for issue in issues)
        return cls(not blocking, tuple(issues))


@dataclass(frozen=True)
class PlausibilityRule:
    """Simple numeric range rule addressed by dotted payload path."""

    path: str
    minimum: float | None = None
    maximum: float | None = None
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: str = "out_of_range"


def _lookup(payload: Mapping[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def check_plausibility(
    payload: Mapping[str, Any], rules: list[PlausibilityRule]
) -> ValidationResult:
    """Run configured plausibility rules against a payload."""
    issues: list[ValidationIssue] = []
    for rule in rules:
        raw = _lookup(payload, rule.path)
        value = raw.get("value") if isinstance(raw, Mapping) and "value" in raw else raw
        if not isinstance(value, int | float):
            continue
        below = rule.minimum is not None and value < rule.minimum
        above = rule.maximum is not None and value > rule.maximum
        if below or above:
            issues.append(
                ValidationIssue(
                    severity=rule.severity,
                    code=rule.code,
                    message=f"{rule.path}={value} is outside plausible range.",
                    path=rule.path,
                    repair_suggestion="Clamp value to the configured plausible range.",
                )
            )
    return ValidationResult.from_issues(issues)


def attempt_local_repair(
    payload: Mapping[str, Any], rules: list[PlausibilityRule]
) -> ValidationResult:
    """Attempt local repair for error-level numeric range violations."""
    repaired: dict[str, Any] = dict(payload)
    issues: list[ValidationIssue] = []
    for rule in rules:
        if rule.severity is ValidationSeverity.FATAL:
            continue
        raw = _lookup(repaired, rule.path)
        value = raw.get("value") if isinstance(raw, Mapping) and "value" in raw else raw
        if not isinstance(value, int | float):
            continue
        new_value = value
        if rule.minimum is not None:
            new_value = max(new_value, rule.minimum)
        if rule.maximum is not None:
            new_value = min(new_value, rule.maximum)
        if new_value != value:
            issues.append(
                ValidationIssue(rule.severity, rule.code, "Value repaired locally.", rule.path)
            )
            # Conservative shallow repair for top-level or quantity-like dictionaries.
            parts = rule.path.split(".")
            target: dict[str, Any] = repaired
            for part in parts[:-1]:
                child = target.get(part)
                if not isinstance(child, dict):
                    break
                target = child
            leaf = target.get(parts[-1])
            if isinstance(leaf, dict) and "value" in leaf:
                leaf["value"] = new_value
            else:
                target[parts[-1]] = new_value
    return ValidationResult(True, tuple(issues), repaired)
