# Universe Generation Pipeline

Universe Gen is a Python package for building a staged universe-generation pipeline. The project is intended to provide deterministic, validated building blocks for procedurally creating astrophysical structures and their supporting metadata.

## Purpose

The pipeline will coordinate numerical modeling, schema-backed data exchange, validation, and stage orchestration so that later work can focus on domain-specific generation logic. This repository currently establishes the foundational project layout and development tooling needed before implementing those stages.

## Architecture Overview

The source package lives under `src/universe_gen/` and is organized around pipeline responsibilities:

- `core/` — shared primitives, constants, domain models, and utility code used across the pipeline.
- `stages/` — generation stages that transform inputs into progressively richer universe artifacts.
- `schemas/` — JSON Schema and Pydantic schema definitions for structured inputs and outputs.
- `validation/` — validation helpers and rules that enforce schema and domain constraints.
- `pipeline/` — orchestration code for composing and executing generation stages.

Tests mirror the source layout under `tests/` so each package area has a corresponding place for unit and integration coverage.

## Development Setup

This project requires Python 3.11 or newer.

Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the package with development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the standard checks:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## Tooling

Configuration is centralized in `pyproject.toml`:

- Ruff provides linting and formatting.
- Mypy provides strict static type checking.
- Pytest is configured as the test framework.
- Setuptools builds the package from the `src/` layout.
