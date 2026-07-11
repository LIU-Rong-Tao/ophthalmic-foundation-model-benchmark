"""Build-time synchronization for packaged registry resources."""

import shutil
from pathlib import Path


def sync_registry_data(project_root: Path | None = None) -> None:
    """Copy the authoritative root registry into package data deterministically."""

    root = project_root or Path(__file__).resolve().parent
    source = root / "registry"
    target = root / "ophbench" / "_registry_data"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "__init__.py").write_text(
        '"""Generated package resources synchronized from the root registry."""\n',
        encoding="utf-8",
    )
    for directory in ("models", "checkpoints", "schemas", "candidates", "datasets", "tasks"):
        source_directory = source / directory
        if source_directory.exists():
            shutil.copytree(source_directory, target / directory)
            (target / directory / "__init__.py").write_text(
                '"""Generated registry resource directory."""\n', encoding="utf-8"
            )
