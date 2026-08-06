"""Abstract stage contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from universe_gen.validation.plausibility import ValidationResult


@dataclass(frozen=True)
class StageConfig:
    """Stage-specific generation and validation configuration."""

    generation_parameters: dict[str, Any] = field(default_factory=dict)
    validation_rules: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageInput:
    """Base stage input carrying provenance."""

    id: str
    provenance: dict[str, Any]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageOutput:
    """Base stage output carrying provenance."""

    id: str
    provenance: dict[str, Any]
    payload: dict[str, Any] = field(default_factory=dict)


class Stage(ABC):
    """Abstract pipeline stage interface."""

    name: ClassVar[str]
    version: ClassVar[str] = "0.1.0"
    input_schema: ClassVar[str | None] = None
    output_schema: ClassVar[str]

    def __init__(self, config: StageConfig | None = None) -> None:
        self.config = config or StageConfig()

    @abstractmethod
    def generate(self, stage_input: StageInput | None = None) -> StageOutput:
        """Generate this stage's output."""

    @abstractmethod
    def validate(self, output: StageOutput) -> ValidationResult:
        """Validate this stage's output."""

    @abstractmethod
    def repair(self, output: StageOutput, result: ValidationResult) -> StageOutput:
        """Repair a locally repairable validation result."""

    def serialize(self, output: StageOutput) -> dict[str, Any]:
        """Serialize stage output."""
        return {"id": output.id, "provenance": output.provenance, **output.payload}

    def deserialize(self, payload: dict[str, Any]) -> StageOutput:
        """Deserialize stage output."""
        return StageOutput(str(payload["id"]), dict(payload["provenance"]), dict(payload))
