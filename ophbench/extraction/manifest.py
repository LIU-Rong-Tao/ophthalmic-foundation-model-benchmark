from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_directory(input_dir: Path) -> list[dict[str, str]]:
    root = input_dir.resolve()
    if not root.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    records = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        records.append(
            {
                "sample_id": relative,
                "relative_path": relative,
                "source_path": str(path),
                "extension": path.suffix.lower(),
                "file_size": str(path.stat().st_size),
            }
        )
    return records


def load_manifest(path: Path, path_column: str, id_column: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = {path_column, id_column} - fields
        if missing:
            raise ValueError(f"Manifest is missing required columns: {', '.join(sorted(missing))}")
        records = []
        for index, row in enumerate(reader):
            source = Path(row[path_column]).expanduser()
            sample_id = (row.get(id_column) or "").strip()
            if not sample_id:
                raise ValueError(f"Manifest row {index + 2} has an empty {id_column}")
            records.append(
                {
                    "sample_id": sample_id,
                    "relative_path": row.get("relative_path") or source.name,
                    "source_path": str(source),
                    "extension": source.suffix.lower(),
                    "file_size": str(source.stat().st_size) if source.is_file() else "",
                }
            )
    return records


def write_input_manifest(records: list[dict[str, str]], destination: Path) -> str:
    fields = ["sample_id", "relative_path", "source_path", "extension", "file_size"]
    destination.write_bytes(serialized_manifest(records, fields))
    return sha256_text(destination)


def serialized_manifest(records: list[dict[str, str]], fields: list[str] | None = None) -> bytes:
    fields = fields or ["sample_id", "relative_path", "source_path", "extension", "file_size"]
    handle = io.StringIO(newline="")
    try:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
        return handle.getvalue().encode("utf-8")
    finally:
        handle.close()
