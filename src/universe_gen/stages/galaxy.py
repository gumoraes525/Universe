"""Galaxy stage stub."""

from __future__ import annotations

from datetime import UTC, datetime

from universe_gen.stages.base import Stage, StageInput, StageOutput
from universe_gen.validation.plausibility import ValidationResult
from universe_gen.validation.validator import validate_schema


class GalaxyStage(Stage):
    """Placeholder implementation for the Galaxy stage."""

    name = "galaxy"
    input_schema = "stages/galaxy/galaxy_input.schema.json"
    output_schema = "stages/galaxy/galaxy_output.schema.json"

    def generate(self, stage_input: StageInput | None = None) -> StageOutput:
        """Generate placeholder output for interface integration."""
        entity_id = stage_input.id if stage_input else "universe"
        provenance = {
            "seed_chain": [{"key": self.name, "entropy": 0}],
            "generated_at": datetime.now(UTC).isoformat(),
            "generator_version": self.version,
            "stage": self.name,
        }
        payload: dict[str, object] = {"objects": []}
        return StageOutput(entity_id, provenance, payload)

    def validate(self, output: StageOutput) -> ValidationResult:
        """Validate placeholder output against the stage output schema."""
        return validate_schema(self.serialize(output), self.output_schema)

    def repair(self, output: StageOutput, result: ValidationResult) -> StageOutput:
        """Return output unchanged until stage-specific repair rules exist."""
        _ = result
        return output
