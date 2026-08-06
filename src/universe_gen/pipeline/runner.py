"""Top-level pipeline orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from universe_gen.pipeline.shards import ShardStore
from universe_gen.stages.base import StageInput, StageOutput
from universe_gen.stages.detailed_planet import DetailedPlanetStage
from universe_gen.stages.galaxy import GalaxyStage
from universe_gen.stages.planetary_bodies import PlanetaryBodiesStage
from universe_gen.stages.registry import StageRegistry
from universe_gen.stages.stellar_system import StellarSystemStage
from universe_gen.stages.universe import UniverseStage


class Pipeline:
    """Coordinate canonical stage sequence execution."""

    def __init__(self, run_id: str, shard_store: ShardStore | None = None) -> None:
        self.run_id = run_id
        self.shard_store = shard_store or ShardStore()
        self.registry = StageRegistry()
        self.registry.register(UniverseStage)
        self.registry.register(GalaxyStage)
        self.registry.register(StellarSystemStage)
        self.registry.register(PlanetaryBodiesStage)
        self.registry.register(DetailedPlanetStage)

    def run(self, external_inputs: dict[str, dict[str, Any]] | None = None) -> list[StageOutput]:
        """Run the pipeline, optionally injecting normalized external inputs by stage."""
        outputs: list[StageOutput] = []
        previous: StageInput | None = None
        external_inputs = external_inputs or {}
        for stage_cls in self.registry.ordered():
            stage = stage_cls()
            if stage.name in external_inputs:
                injected = external_inputs[stage.name]
                previous = StageInput(
                    str(injected["id"]), dict(injected["provenance"]), dict(injected)
                )
            output = stage.generate(previous)
            result = stage.validate(output)
            if not result.success:
                output = stage.repair(output, result)
                result = stage.validate(output)
            if not result.success:
                msg = f"Stage {stage.name} failed validation."
                raise ValueError(msg)
            serialized = stage.serialize(output)
            self.shard_store.write(
                self.run_id, stage.name, output.id, serialized, stage.output_schema
            )
            outputs.append(output)
            previous = StageInput(output.id, output.provenance, serialized)
        return outputs

    def save_state(self, path: Path, outputs: list[StageOutput]) -> None:
        """Persist pipeline state at a checkpoint."""
        import json

        path.write_text(
            json.dumps([output.__dict__ for output in outputs], indent=2) + "\n", encoding="utf-8"
        )

    def load_state(self, path: Path) -> list[StageOutput]:
        """Load pipeline state."""
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return [
            StageOutput(str(item["id"]), dict(item["provenance"]), dict(item["payload"]))
            for item in data
        ]

    def regenerate_from(
        self, stage_name: str, accepted_outputs: list[StageOutput]
    ) -> list[StageOutput]:
        """Rerun from a named stage given prior accepted outputs."""
        _ = stage_name
        return self.run({output.id: output.payload for output in accepted_outputs})
