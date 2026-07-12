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


EVIDENCE_LABELS = {
    "pending": "待核验",
    "verified": "已核验",
    "blocked": "受阻",
    "not_applicable": "不适用",
}
ACCESS_LABELS = {
    "open": "登记为开放",
    "auth_required": "需认证/申请",
    "gated": "受限访问",
    "application_required": "需申请",
    "unavailable": "暂不可用",
    "unknown": "待核验",
}


def _evidence(record, field):
    verification = getattr(record, "verification", None)
    return getattr(verification, field, "pending") if verification else "pending"


def _core_architecture(model):
    details = model.architecture_details
    if details and details.encoder_variant:
        objective = f" / {details.pretraining_objective}" if details.pretraining_objective else ""
        return f"{details.encoder_variant}{objective}"
    return model.architecture if len(model.architecture) <= 48 else model.architecture[:47] + "…"


def _group_name(model):
    image_modalities = [item for item in model.modalities if item != "text"]
    if "text" in model.modalities:
        return "视觉语言模型"
    if len(image_modalities) > 1:
        return "多模态眼科模型"
    if "CFP" in image_modalities:
        return "CFP 模型"
    if "OCT" in image_modalities:
        return "OCT 模型"
    return "其他眼科模型"


def _runtime_status(model):
    if model.implementation.smoke_test_status == "passed":
        return "可提取特征"
    if model.implementation.adapter_status == "implemented":
        return "Adapter 已实现，待验证"
    return "尚不可运行"


def _model_zoo(models, checkpoints):
    counts = {}
    for model in models:
        counts[model.verification_status] = counts.get(model.verification_status, 0) + 1
    model_checkpoints = {}
    for checkpoint in checkpoints:
        model_checkpoints.setdefault(checkpoint.model_id, []).append(checkpoint)
    verification_labels = {
        "seed_unverified": "待核验",
        "partially_verified": "部分已核验",
        "verified": "已核验",
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
        ]
    )
    for group in (
        "CFP 模型",
        "OCT 模型",
        "多模态眼科模型",
        "视觉语言模型",
        "其他眼科模型",
    ):
        grouped = [model for model in models if _group_name(model) == group]
        if not grouped:
            continue
        lines.extend(
            [
                "",
                f"## {group}",
                "",
                "| 模型 | 模态 | 核心架构 | Checkpoint | 权重访问 | 核验状态 | 运行状态 |",
                "|---|---|---|---:|---|---|---|",
            ]
        )
        for model in grouped:
            assets = model_checkpoints.get(model.model_id, [])
            access = "、".join(
                sorted({ACCESS_LABELS.get(item.access_type, item.access_type) for item in assets})
            )
            lines.append(
                f"| [{model.model_name}](model_cards/{model.model_id}.md) | "
                f"{', '.join(model.modalities)} | {_core_architecture(model)} | {len(assets)} | "
                f"{access or '待核验'} | "
                f"{verification_labels.get(model.verification_status, model.verification_status)} "
                "| "
                f"{_runtime_status(model)} |"
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


def _model_card(model, checkpoints):
    axes = (
        ("paper", "论文"),
        ("code", "官方代码"),
        ("checkpoint_url", "Checkpoint 入口"),
        ("checkpoint_file", "Checkpoint 文件"),
        ("license", "许可证"),
        ("preprocessing", "原生预处理"),
        ("adapter", "Adapter"),
        ("feature_output", "特征输出"),
    )
    latest = max(
        (item.last_verified for item in checkpoints if item.last_verified),
        default="尚未登记",
    )
    preprocessing_sources = [
        item.preprocessing.source
        for item in checkpoints
        if item.preprocessing and item.preprocessing.source
    ]
    evidence = {
        "paper": model.paper_url or "尚未登记",
        "code": model.code_url or "尚未登记",
        "checkpoint_url": f"{sum(bool(item.weight_url) for item in checkpoints)} 个已登记入口",
        "checkpoint_file": ", ".join(
            f"{item.checkpoint_id}:{item.sha256[:12]}…" for item in checkpoints if item.sha256
        )
        or "尚未登记",
        "license": model.license or "尚未登记",
        "preprocessing": ", ".join(preprocessing_sources) or "尚未登记",
        "adapter": model.implementation.adapter_status,
        "feature_output": model.implementation.smoke_test_status,
    }
    lines = [f"<!-- {NOTICE} -->", f"# {model.model_name}", "", "## 模型概览", ""]
    lines.extend(
        [
            f"- **Model ID**：`{model.model_id}`",
            f"- **模型类型**：{model.model_category}",
            f"- **模态**：{', '.join(model.modalities)}",
            f"- **核心架构**：{_core_architecture(model)}",
            f"- **预训练方式**：{model.pretraining_strategy}",
            f"- **当前状态**：{_runtime_status(model)}",
            "",
            "## 官方入口",
            "",
            f"- 论文：{f'[{model.paper_url}]({model.paper_url})' if model.paper_url else '待核验'}",
            f"- 代码：{f'[{model.code_url}]({model.code_url})' if model.code_url else '待核验'}",
            "",
            "## Checkpoint 资产",
            "",
            "| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |",
            "|---|---|---|---|---|---|",
        ]
    )
    for checkpoint in checkpoints:
        source = (
            f"[{checkpoint.provider}]({checkpoint.weight_url})"
            if checkpoint.weight_url
            else checkpoint.provider
        )
        file_status = EVIDENCE_LABELS[_evidence(checkpoint, "checkpoint_file")]
        adapter = "已验证" if (
            model.implementation.smoke_test_status == "passed"
            and _evidence(checkpoint, "adapter") == "verified"
        ) else "未验证"
        lines.append(
            f"| `{checkpoint.checkpoint_id}` / {checkpoint.checkpoint_name} | "
            f"{', '.join(checkpoint.modalities)} | {source} | "
            f"{ACCESS_LABELS.get(checkpoint.access_type, checkpoint.access_type)} | "
            f"{file_status} | {adapter} |"
        )
    lines.extend(["", "## 输入与原生预处理", ""])
    for checkpoint in checkpoints:
        lines.append(f"### `{checkpoint.checkpoint_id}`")
        if checkpoint.input:
            size = " × ".join(map(str, checkpoint.input.size or ())) or "待核验"
            lines.append(f"- 输入：{checkpoint.input.color_space or '待核验'}，{size}")
        else:
            lines.append(f"- 输入：{checkpoint.input_size or '待核验'}")
        if checkpoint.preprocessing and checkpoint.preprocessing.resize:
            resize = checkpoint.preprocessing.resize
            resize_size = " × ".join(map(str, resize.size or ())) or "待核验"
            lines.append(f"- Resize：{resize_size}，{resize.interpolation or '待核验'}")
        if checkpoint.preprocessing and checkpoint.preprocessing.crop:
            crop = checkpoint.preprocessing.crop
            crop_size = " × ".join(map(str, crop.size or ())) or "待核验"
            lines.append(f"- Crop：{crop.type or '待核验'}，{crop_size}")
        lines.append(f"- 归一化：{checkpoint.normalization or '待核验'}")
        lines.append(
            f"- 预处理核验：{EVIDENCE_LABELS[_evidence(checkpoint, 'preprocessing')]}"
        )
    lines.extend(["", "## 特征输出", ""])
    for checkpoint in checkpoints:
        dimension = checkpoint.embedding_dim if checkpoint.embedding_dim else "待核验"
        lines.append(f"- `{checkpoint.checkpoint_id}`：embedding 维度 {dimension}")
    lines.extend(
        [
            "",
            "## 权重与许可限制",
            "",
            f"- 模型许可证：{model.license or '待核验'}",
            "- 本仓库默认不重新分发第三方权重。",
            "- Adapter smoke 不等于下游任务性能结论。",
            "",
            "## 核验记录",
            "",
            "| 核验项 | 状态 | 证据/记录 | 最近核验 |",
            "|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {label} | {EVIDENCE_LABELS[_evidence(model, field)]} | "
        f"{evidence[field]} | {latest} |"
        for field, label in axes
    )
    pending = [label for field, label in axes if _evidence(model, field) == "pending"]
    lines.extend(["", "## 待核验事项", ""])
    lines.extend([f"- {item}" for item in pending] or ["- 无"])
    lines.extend(["", "[返回 Model Zoo](../MODEL_ZOO.md)", ""])
    return "\n".join(lines)


def _outputs(registry_root):
    models, checkpoints = load_registry(registry_root)
    models = sorted(models, key=lambda x: x.model_id)
    checkpoints = sorted(checkpoints, key=lambda x: x.checkpoint_id)
    model_checkpoints = {
        model.model_id: [item for item in checkpoints if item.model_id == model.model_id]
        for model in models
    }
    outputs = {
        "models.csv": _csv(models),
        "checkpoints.csv": _csv(checkpoints),
        "models.json": _json(models),
        "checkpoints.json": _json(checkpoints),
        "MODEL_ZOO.md": _model_zoo(models, checkpoints),
    }
    outputs.update(
        {
            f"model_cards/{model.model_id}.md": _model_card(
                model, model_checkpoints[model.model_id]
            )
            for model in models
        }
    )
    return (
        models,
        checkpoints,
        outputs,
    )


def build_catalog(
    registry_root: Path, output_dir: Path, check: bool = False, model_zoo_path: Path | None = None
):
    models, checkpoints, outputs = _outputs(registry_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    stale = False
    for name, content in outputs.items():
        if name == "MODEL_ZOO.md":
            target = model_zoo_path or output_dir / name
        elif name.startswith("model_cards/"):
            root = model_zoo_path.parent if model_zoo_path else output_dir
            target = root / name
        else:
            target = output_dir / name
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
