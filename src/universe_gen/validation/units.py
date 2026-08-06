"""SI unit enforcement and astronomical unit conversion helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from astropy import units as u

CANONICAL_UNITS: Final[dict[str, str]] = {
    "mass": "kg",
    "distance": "m",
    "time": "s",
    "temperature": "K",
    "angle": "rad",
    "velocity": "m / s",
    "density": "kg / m3",
    "luminosity": "W",
}

_ALLOWED_BASES: Final[set[u.UnitBase]] = {u.m, u.kg, u.s, u.K, u.A, u.mol, u.cd, u.rad, u.sr}


@dataclass(frozen=True)
class SIQuantity:
    """A quantity serialized with an SI-compatible unit."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        parsed = u.Unit(self.unit)
        if not is_si_unit(parsed):
            msg = f"Unit {self.unit!r} is not an SI unit representation."
            raise ValueError(msg)

    @property
    def quantity(self) -> u.Quantity:
        """Return the corresponding Astropy quantity."""
        return self.value * u.Unit(self.unit)

    def to_json(self) -> dict[str, float | str]:
        """Serialize quantity as a schema-compatible object."""
        return {"value": self.value, "unit": self.unit}

    @classmethod
    def from_quantity(cls, quantity: u.Quantity, quantity_type: str) -> SIQuantity:
        """Convert a quantity to its canonical SI unit for a physical quantity type."""
        target = CANONICAL_UNITS[quantity_type]
        converted = quantity.to(u.Unit(target))
        return cls(float(converted.value), target)


def is_si_unit(unit: u.UnitBase | str) -> bool:
    """Return whether a unit is composed only from SI base units."""
    parsed = u.Unit(unit)
    bases = parsed.decompose().bases
    return all(base in _ALLOWED_BASES for base in bases)


def validate_si_quantity(data: object) -> SIQuantity:
    """Validate a schema-style SI quantity object."""
    if not isinstance(data, dict) or "value" not in data or "unit" not in data:
        msg = "Quantity must be an object containing value and unit."
        raise ValueError(msg)
    return SIQuantity(float(data["value"]), str(data["unit"]))


def convert_to_si(value: float, unit: str, quantity_type: str) -> SIQuantity:
    """Convert a value in a supported unit into a canonical SI representation."""
    return SIQuantity.from_quantity(value * u.Unit(unit), quantity_type)
