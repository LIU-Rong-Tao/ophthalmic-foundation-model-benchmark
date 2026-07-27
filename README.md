# Ophthalmic Foundation Model Benchmark

公开眼科基础模型元数据注册表与统一评测基础设施。v0.2 在稳定注册表消费者 API
之上加入首个真实图像编码器 adapter：RETFound CFP。项目仍不自动下载认证权重，也不将
adapter smoke test 描述为下游 benchmark 结果。

当前 seed 包含 15 个模型和 27 个 checkpoint。YAML 文件是唯一权威数据源，`MODEL_ZOO.md` 与 `catalog/` 均由工具自动生成。

## v0.3 最短入口

本地权重与图像均由调用者显式提供；提取器不会联网下载权重，也不会把原始路径写入 Dashboard 数据。

```powershell
ophbench extract --model retfound --checkpoint-id retfound-cfp --checkpoint .\weights\retfound.pth --input-dir .\images --output-dir .\features\retfound
```

```powershell
ophbench benchmark build --release benchmark\releases\demo-v1.yaml --runs-root benchmark\runs --output benchmark\generated
ophbench dashboard --results benchmark\generated
```

`extract` 输出可恢复的 NPY 分片、样本对齐表、失败记录、运行指纹和 SHA256 清单；只有相同 fingerprint 的未完成运行才可使用 `--resume`。Dashboard 只读取 `benchmark/generated/` 内的静态脱敏 JSON，不能扫描实验目录或重新计算指标。

当前实现的通用提取 Adapter 为 RETFound CFP 和 RETFound-Green。EyeCLIP 需要已核验的官方本地运行时及真实 checkpoint 容器审计，当前状态为 `requires_external_runtime`，不会以普通 CLIP 实现替代。

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

## Frozen Feature Transfer v0.1

`protocols/frozen_feature_transfer_v0_1.yaml` 定义冻结特征迁移评测的唯一协议。第一版仅以
RETFound CFP + APTOS2019 验证协议可执行性和可复现性，角色为
`pilot_protocol_validation`，不得据此形成模型优劣或患者级结论。

协议固定模型原生预处理、冻结 embedding、Logistic Regression、validation Macro-F1
选取 C、test 最终评估一次，以及 image-level bootstrap 95% CI。运行产物默认保存在本地
忽略目录，不提交医学图像、特征、预测或模型权重。

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
