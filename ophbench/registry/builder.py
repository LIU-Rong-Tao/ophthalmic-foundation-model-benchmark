from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

from .loader import load_registry

NOTICE = "AUTO-GENERATED. DO NOT EDIT MANUALLY."


@dataclass(frozen=True)
class BuildResult:
    model_count: int
    checkpoint_count: int
    is_stale: bool = False


def _json(records):
    data = [record.model_dump(mode="json") for record in records]
    return json.dumps({"notice": NOTICE, "records": data}, ensure_ascii=False, indent=2) + "\n"


def _csv(records):
    rows = [record.model_dump(mode="json") for record in records]
    fields = list(rows[0]) if rows else []
    stream = io.StringIO(newline="")
    stream.write(f"# {NOTICE}\n")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value
                for key, value in row.items()
            }
        )
    return stream.getvalue()


def _model_zoo(models, checkpoints):
    counts = {}
    for model in models:
        counts[model.verification_status] = counts.get(model.verification_status, 0) + 1
    access = {}
    for checkpoint in checkpoints:
        access.setdefault(checkpoint.model_id, set()).add(checkpoint.access_type)
    lines = [
        f"<!-- {NOTICE} -->",
        "# Model Zoo",
        "",
        f"Models: **{len(models)}**  ",
        f"Checkpoints: **{len(checkpoints)}**",
        "",
        "## Verification status",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(counts.items()))
    lines.extend(
        [
            "",
            "## Models",
            "",
            "| Model | Year | Venue | Category | Modalities | Runtime phase "
            "| Weight access | Adapter status |",
            "|---|---:|---|---|---|---|---|---|",
        ]
    )
    for model in models:
        label = f"[{model.model_name}]({model.paper_url})" if model.paper_url else model.model_name
        if model.code_url:
            label += f" ([code]({model.code_url}))"
        modalities = ", ".join(model.modalities)
        weight_access = ", ".join(sorted(access.get(model.model_id, {"unknown"})))
        lines.append(
            f"| {label} | {model.year or ''} | {model.venue} | "
            f"{model.model_category} | {modalities} | {model.runtime_phase} | "
            f"{weight_access} | {model.implementation.adapter_status} |"
        )
    lines.extend(
        [
            "",
            "## Important notice",
            "",
            "- Information originates from the seed spreadsheet and remains unverified "
            "unless explicitly marked otherwise.",
            "- Unverified entries must not be treated as official confirmation.",
            "- This repository does not redistribute third-party weights by default.",
            "- `reported_summary` records claims from the paper/spreadsheet; it is not a "
            "reproduced result from this project.",
            "",
        ]
    )
    return "\n".join(lines)


def _outputs(registry_root):
    models, checkpoints = load_registry(registry_root)
    models = sorted(models, key=lambda x: x.model_id)
    checkpoints = sorted(checkpoints, key=lambda x: x.checkpoint_id)
    return (
        models,
        checkpoints,
        {
            "models.csv": _csv(models),
            "checkpoints.csv": _csv(checkpoints),
            "models.json": _json(models),
            "checkpoints.json": _json(checkpoints),
            "MODEL_ZOO.md": _model_zoo(models, checkpoints),
        },
    )


def build_catalog(
    registry_root: Path, output_dir: Path, check: bool = False, model_zoo_path: Path | None = None
):
    models, checkpoints, outputs = _outputs(registry_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    stale = False
    for name, content in outputs.items():
        target = (
            (model_zoo_path or output_dir / name) if name == "MODEL_ZOO.md" else output_dir / name
        )
        if check:
            stale |= not target.exists() or target.read_text(encoding="utf-8") != content
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="")
    return BuildResult(len(models), len(checkpoints), stale)


def catalog_is_current(registry_root: Path, output_dir: Path, model_zoo_path: Path):
    return not build_catalog(
        registry_root, output_dir, check=True, model_zoo_path=model_zoo_path
    ).is_stale
