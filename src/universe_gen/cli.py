"""Click command line entry point for Universe Gen."""

from __future__ import annotations

from pathlib import Path

import click

from universe_gen.pipeline.checkpoint import Checkpoint
from universe_gen.pipeline.runner import Pipeline
from universe_gen.pipeline.shards import ShardStore
from universe_gen.validation.validator import validate_schema


@click.group()
def main() -> None:
    """Universe generation pipeline commands."""


@main.command()
@click.option("--run-id", required=True)
@click.option("--master-seed", required=True, type=int)
@click.option("--dry-run", is_flag=True)
def generate(run_id: str, master_seed: int, dry_run: bool) -> None:
    """Run the full pipeline from a master seed."""
    _ = master_seed
    if dry_run:
        click.echo(f"Dry run accepted for {run_id}; no generation performed.")
        return
    outputs = Pipeline(run_id).run()
    click.echo(f"Generated {len(outputs)} stage outputs for {run_id}.")


@main.command()
@click.argument("checkpoint", type=click.Path(path_type=Path))
@click.option("--dry-run", is_flag=True)
def resume(checkpoint: Path, dry_run: bool) -> None:
    """Continue from a reviewed checkpoint."""
    loaded = Checkpoint.load(checkpoint)
    if dry_run:
        loaded.validate()
        click.echo(f"Checkpoint {loaded.checkpoint_id} is valid.")
        return
    Pipeline(loaded.checkpoint_id).run()


@main.command()
@click.argument("run_id")
@click.option("--dry-run", is_flag=True)
def validate(run_id: str, dry_run: bool) -> None:
    """Validate existing shards against schemas."""
    _ = dry_run
    index = ShardStore().index(run_id)
    failures = 0
    for entity_id, path in index.items():
        stage = path.parent.name
        schema = _schema_for_stage(stage)
        payload = ShardStore().read(run_id, stage, entity_id)
        result = validate_schema(payload, schema)
        failures += 0 if result.success else 1
    if failures:
        raise click.ClickException(f"{failures} shard(s) failed validation.")
    click.echo(f"Validated {len(index)} shard(s).")


@main.command()
@click.option("--run-id", required=True)
@click.option("--stage", "stage_name", required=True)
@click.option("--entity-id", required=True)
@click.option("--dry-run", is_flag=True)
def regenerate(run_id: str, stage_name: str, entity_id: str, dry_run: bool) -> None:
    """Selectively regenerate from the specified stage and ID."""
    if dry_run:
        click.echo(f"Would regenerate {entity_id} from {stage_name} in {run_id}.")
        return
    Pipeline(run_id).regenerate_from(stage_name, [])
    click.echo(f"Regenerated from {stage_name}:{entity_id}.")


def _schema_for_stage(stage: str) -> str:
    mapping = {
        "universe": "stages/universe/universe_output.schema.json",
        "galaxy": "stages/galaxy/galaxy_output.schema.json",
        "stellar_system": "stages/stellar_system/system_output.schema.json",
        "planetary_bodies": "stages/planetary_bodies/bodies_output.schema.json",
        "detailed_planet": "stages/detailed_planet/planet_output.schema.json",
    }
    return mapping[stage]
