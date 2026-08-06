# Tool Target Specifications

This document defines future-facing derived outputs produced from canonical JSON shards. These targets must not replace the canonical schemas; they are downstream transformations.

## 3D Review Outputs

- Universe stage: overview metadata suitable for scale-navigation scenes and cosmic parameter overlays.
- Galaxy stage: point-cloud or instanced render data for large-scale stellar distribution review.
- Stellar system stage: orbit tracks, star markers, habitable-zone guides, and constraint annotations.
- Planetary bodies stage: body meshes or proxy spheres with orbital element visualization.
- Detailed planet stage: surface tiles, atmosphere shells, geology layers, and landmark annotations.

## Atlas-Style Map Products

Applicable stages should provide deterministic map products derived from canonical JSON:

- Galaxy atlases: sector maps with density and population overlays.
- Stellar system atlases: top-down orbital maps with body labels and stable IDs.
- Planetary atlases: equirectangular and tiled projections for terrain, biome, geology, and atmosphere data.

## Unreal-Facing Derived Formats

Future Unreal exports should include:

- Stable object names based on hierarchical IDs.
- SI-unit transforms converted to engine scale at the boundary.
- Material parameter payloads derived from canonical physical properties.
- Provenance metadata embedded alongside assets for traceability.

## Transformation Pipeline

1. Read canonical JSON shards from `output/{run_id}/{stage}/{entity_id}.json`.
2. Validate shards against authoritative JSON Schemas.
3. Convert SI quantities to target engine or visualization units at the final export boundary.
4. Emit derived artifacts with sidecar provenance and source shard references.
5. Revalidate generated sidecars before importing into external tools.
