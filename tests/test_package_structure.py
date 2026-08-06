"""Smoke tests for the foundational package layout."""

import importlib


def test_universe_gen_packages_import() -> None:
    """All foundational package namespaces should be importable."""
    packages = [
        "universe_gen",
        "universe_gen.core",
        "universe_gen.stages",
        "universe_gen.schemas",
        "universe_gen.validation",
        "universe_gen.pipeline",
    ]

    for package in packages:
        assert importlib.import_module(package)
