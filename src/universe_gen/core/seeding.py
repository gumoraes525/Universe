"""Deterministic, order-independent seeding utilities."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Any

from numpy.random import Generator, SeedSequence, default_rng


def _key_entropy(child_key: str) -> int:
    digest = blake2b(child_key.encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(digest, "big", signed=False)


@dataclass(frozen=True)
class MasterSeed:
    """Root seed that derives child seed sequences from stable child keys."""

    entropy: int
    spawn_key: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.entropy < 0:
            msg = "Seed entropy must be non-negative."
            raise ValueError(msg)

    @property
    def seed_sequence(self) -> SeedSequence:
        """Return a NumPy seed sequence for this seed state."""
        return SeedSequence(self.entropy, spawn_key=self.spawn_key)

    def child(self, child_key: str) -> MasterSeed:
        """Derive a child seed without depending on sibling creation order."""
        if not child_key:
            msg = "Child seed key must be non-empty."
            raise ValueError(msg)
        return MasterSeed(self.entropy, (*self.spawn_key, _key_entropy(child_key)))

    def rng(self) -> Generator:
        """Create a NumPy generator for this seed state."""
        return default_rng(self.seed_sequence)

    def to_json(self) -> dict[str, Any]:
        """Serialize seed state to JSON-compatible data."""
        return {"entropy": self.entropy, "spawn_key": list(self.spawn_key)}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MasterSeed:
        """Deserialize seed state from JSON-compatible data."""
        return cls(
            entropy=int(data["entropy"]), spawn_key=tuple(int(v) for v in data.get("spawn_key", []))
        )


@dataclass(frozen=True)
class SeededGenerator:
    """Stage-specific deterministic random generator wrapper."""

    seed: MasterSeed
    stage_key: str

    @property
    def stage_seed(self) -> MasterSeed:
        """Derived seed for this stage."""
        return self.seed.child(self.stage_key)

    def rng(self, local_key: str | None = None) -> Generator:
        """Return a deterministic RNG for the stage or local child key."""
        seed = self.stage_seed if local_key is None else self.stage_seed.child(local_key)
        return seed.rng()

    def to_json(self) -> dict[str, Any]:
        """Serialize wrapper state."""
        return {"seed": self.seed.to_json(), "stage_key": self.stage_key}
