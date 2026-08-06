"""Stage registry and canonical ordering."""

from __future__ import annotations

from universe_gen.stages.base import Stage

CANONICAL_STAGE_ORDER = (
    "universe",
    "galaxy",
    "stellar_system",
    "planetary_bodies",
    "detailed_planet",
)


class StageRegistry:
    """Registry for stage lookup and ordering validation."""

    def __init__(self) -> None:
        self._stages: dict[str, type[Stage]] = {}

    def register(self, stage: type[Stage]) -> None:
        """Register a stage class by name."""
        self._stages[stage.name] = stage

    def get(self, name: str) -> type[Stage]:
        """Return a stage class by name."""
        return self._stages[name]

    def ordered(self) -> list[type[Stage]]:
        """Return registered stages in canonical order."""
        return [self._stages[name] for name in CANONICAL_STAGE_ORDER if name in self._stages]

    def validate_ordering(self, names: list[str]) -> bool:
        """Validate that names follow canonical order."""
        positions = [CANONICAL_STAGE_ORDER.index(name) for name in names]
        return positions == sorted(positions)

    def validate_handoffs(self) -> bool:
        """Verify adjacent stage schema references are compatible by convention."""
        stages = self.ordered()
        for previous, current in zip(stages, stages[1:], strict=False):
            if current.input_schema is None or previous.output_schema is None:
                return False
        return True
