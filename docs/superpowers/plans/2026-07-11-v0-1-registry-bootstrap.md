# v0.1 Registry Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible v0.1 registry and generated catalog for 15 seed ophthalmic foundation models and 27 checkpoints without implementing model inference.

**Architecture:** Per-model and per-checkpoint YAML files are the source of truth. Pydantic models validate data, an Excel importer deterministically regenerates seed YAML, and a catalog builder produces Markdown/CSV/JSON artifacts. A Typer CLI exposes import, validate, build, inspect, and doctor operations; adapter interfaces remain implementation-free.

**Tech Stack:** Python 3.11, Pydantic 2, PyYAML, openpyxl, Typer, Rich, pytest, Ruff.

---

### Task 1: Project scaffold and safety

- [ ] Anchor runtime ignore rules at the repository root and verify registry checkpoint YAML remains trackable.
- [ ] Add `pyproject.toml`, package directories, scripts, documentation directories, and the copied seed workbook.
- [ ] Commit as `chore: scaffold registry-based project structure`.

### Task 2: Test-first registry core

- [ ] Write failing tests for importer counts/IDs, schema failures, cross-record validation, duplicate IDs, URL rules, and secret/path rejection.
- [ ] Run focused tests and confirm failure because registry modules do not exist.
- [ ] Implement Pydantic schemas, YAML loader, validator, deterministic Excel importer, JSON Schema exports, and manifest generation.
- [ ] Run focused tests until green.
- [ ] Commit as `feat: add registry schemas importer and validation`.

### Task 3: Seed registry

- [ ] Copy the workbook to `seed/ophthalmic_models_seed_v0.xlsx` and calculate SHA256.
- [ ] Run importer to generate exactly 15 model YAML and 27 checkpoint YAML with seed-unverified provenance.
- [ ] Validate offline and verify no URL is accessed or weight is downloaded.
- [ ] Commit as `data: import initial ophthalmic model registry`.

### Task 4: Test-first catalog, CLI, and adapter contracts

- [ ] Write failing tests for stable catalog output, stale detection, DummyAdapter registration, and unimplemented-adapter diagnostics.
- [ ] Implement deterministic catalog generation, Typer commands, doctor output, abstract adapter interfaces, and factory errors.
- [ ] Generate `MODEL_ZOO.md` and catalog CSV/JSON; run build check twice for idempotence.
- [ ] Add lightweight script wrappers, concise project documentation, Makefile, and GitHub Actions.
- [ ] Run Ruff and pytest until green.
- [ ] Commit as `ci: add catalog generation tests and registry workflow`.

### Task 5: Acceptance and delivery

- [ ] Run `ruff check .`, registry validation, catalog build check, `pytest -q`, CLI smoke commands, and `git check-ignore`.
- [ ] Audit tracked files for model binaries, medical data, tokens, caches, and unexpectedly large files.
- [ ] Review every acceptance criterion and record any intentional deviation.
- [ ] Push only `feat/v0.1-registry-bootstrap` when authentication permits; never merge, tag, release, force-push, or push main.
