from __future__ import annotations

from pathlib import Path

from .writer import atomic_json


def load_state(output_dir: Path):
    path = output_dir / "state.json"
    if not path.is_file():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def save_state(output_dir: Path, **payload) -> None:
    atomic_json(output_dir / "state.json", payload)
