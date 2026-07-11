# Ophthalmic Foundation Model Benchmark

公开眼科基础模型元数据注册表与统一评测基础设施。v0.2 在稳定注册表消费者 API
之上加入首个真实图像编码器 adapter：RETFound CFP。项目仍不自动下载认证权重，也不将
adapter smoke test 描述为下游 benchmark 结果。

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

## RETFound CFP adapter

注册表功能保持轻量；仅在运行 adapter 时安装可选依赖：

```powershell
pip install -e ".[retfound]"
```

权重必须由调用者明确提供，本项目不会自动下载 gated checkpoint：

```python
from ophbench import load_adapter

adapter = load_adapter(
    model_id="retfound",
    checkpoint_id="retfound-cfp",
    checkpoint_path="/path/to/RETFound_mae_natureCFP.pth",
    device="cuda:0",
).load()
embedding = adapter.encode_image(image)
assert embedding.shape[-1] == 1024
```
