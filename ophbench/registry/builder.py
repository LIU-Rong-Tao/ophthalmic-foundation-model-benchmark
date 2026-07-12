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
    model_checkpoints = {}
    for checkpoint in checkpoints:
        access.setdefault(checkpoint.model_id, set()).add(checkpoint.access_type)
        model_checkpoints.setdefault(checkpoint.model_id, []).append(checkpoint)
    verification_labels = {
        "seed_unverified": "待核验",
        "partially_verified": "部分已核验",
        "verified": "已核验",
    }
    access_labels = {
        "open": "登记为开放",
        "auth_required": "需认证/申请",
        "unknown": "待核验",
    }
    lines = [
        f"<!-- {NOTICE} -->",
        "# 眼科基础模型目录",
        "",
        f"Models: **{len(models)}**  ",
        f"Checkpoints: **{len(checkpoints)}**",
        "",
        "本页展示模型资产的收录与核验进度。**已收录不等于已支持运行**。",
        "",
        "## 核验概览",
        "",
    ]
    lines.extend(
        f"- {verification_labels.get(key, key)}：{value} 个模型"
        for key, value in sorted(counts.items())
    )
    lines.extend(
        [
            "",
            "## 模型资产",
            "",
            "| 模型 | 模态 | Checkpoint | 权重访问 | 信息核验 | 权重核验 | Adapter | 特征提取 |",
            "|---|---|---:|---|---|---|---|---|",
        ]
    )
    for model in models:
        label = f"[{model.model_name}]({model.paper_url})" if model.paper_url else model.model_name
        if model.code_url:
            label += f" ([code]({model.code_url}))"
        modalities = ", ".join(model.modalities)
        weight_access = "、".join(
            access_labels.get(item, item)
            for item in sorted(access.get(model.model_id, {"unknown"}))
        )
        checkpoints_for_model = model_checkpoints.get(model.model_id, [])
        weight_status = "待核验"
        if any(
            checkpoint.sha256
            and checkpoint.verification_status in {"partially_verified", "verified"}
            for checkpoint in checkpoints_for_model
        ):
            weight_status = "文件已核验"
        adapter_status = (
            "已实现"
            if model.implementation.adapter_status == "implemented"
            else "未实现"
        )
        feature_status = (
            "已验证"
            if model.implementation.smoke_test_status == "passed"
            else "未验证"
        )
        lines.append(
            f"| {label} | {modalities} | {len(checkpoints_for_model)} | {weight_access} | "
            f"{verification_labels.get(model.verification_status, model.verification_status)} | "
            f"{weight_status} | {adapter_status} | {feature_status} |"
        )
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 待核验记录不能视为官方确认信息。",
            "- “登记为开放”只表示 seed 中的访问记录，不代表权重和许可证已核验。",
            "- 本仓库默认不重新分发第三方权重。",
            "- 论文报告结果不等于本项目复现结果。",
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
