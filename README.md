# Ophthalmic Foundation Model Benchmark

公开眼科基础模型元数据注册表与统一评测基础设施。v0.1 只提供注册表、seed 导入、校验、模型目录和 adapter 接口，**不包含真实模型加载、权重下载或 benchmark 结果**。

当前 seed 包含 15 个模型和 27 个 checkpoint。YAML 文件是唯一权威数据源，`MODEL_ZOO.md` 与 `catalog/` 均由工具自动生成。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
ophbench registry validate
ophbench catalog build --check
ophbench list-models
ophbench show-model retfound
ophbench doctor --model retfound
```

重新导入 seed：

```powershell
ophbench registry import-seed --input seed/ophthalmic_models_seed_v0.xlsx
ophbench catalog build
```

模型总览见 [MODEL_ZOO.md](MODEL_ZOO.md)。第三方权重默认不在本仓库重新分发，用户须从官方来源获取并遵守各自许可证，详见 [权重政策](docs/weight_policy.md)。开发路线见 [Roadmap](docs/roadmap.md)。
