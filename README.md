# Ophthalmic Foundation Model Benchmark

公开眼科基础模型元数据注册表、统一冻结特征提取与多任务评测基础设施。v0.3 已实现
RETFound CFP、RETFound-Green 和 EyeCLIP 视觉编码器 Adapter。项目不自动下载权重，
也不将 Adapter smoke test 描述为下游 Benchmark 结果。

当前 seed 包含 15 个模型和 27 个 checkpoint。YAML 文件是唯一权威数据源，`MODEL_ZOO.md` 与 `catalog/` 均由工具自动生成。

## v0.3 最短入口

本地权重仅需配置一次。Linux 默认读取 `~/.config/ophbench/config.yaml`，也可通过
`OPHBENCH_CONFIG` 指向其他本地配置：

```yaml
device: cuda:0
batch_size: 8
checkpoints:
  retfound-cfp: /path/to/RETFound_mae_natureCFP.pth
  retfound-green-v0.1: /path/to/retfoundgreen_statedict.pth
  eyeclip-default: /path/to/eyeclip.pt
```

配置后，目录输入的最短命令为：

```bash
ophbench extract retfound-cfp \
  --input /path/to/images \
  --output /path/to/features
```

`retfound-green` 与 `eyeclip` 也可直接作为 profile；模型 profile 决定 Adapter、
checkpoint 配置及模型原生预处理。原有长命令保持兼容：

```bash
ophbench extract \
  --model retfound \
  --checkpoint-id retfound-cfp \
  --checkpoint /path/to/RETFound_mae_natureCFP.pth \
  --input-dir /path/to/images \
  --output-dir /path/to/features
```

```bash
ophbench benchmark build \
  --release benchmark/releases/2026.07.yaml \
  --runs-root benchmark/runs \
  --output benchmark/generated
ophbench dashboard --results benchmark/generated
```

`extract` 输出可恢复的 NPY 分片、样本对齐表、失败记录、运行指纹和 SHA256 清单；只有相同 fingerprint 的未完成运行才可使用 `--resume`。Dashboard 只读取 `benchmark/generated/` 内的静态脱敏 JSON，不能扫描实验目录或重新计算指标。

当前三个 Adapter 均经过真实本地 checkpoint smoke；EyeCLIP 仅实现官方视觉分支，
严格排除文本编码器和 MAE decoder。权重不会提交或重新分发。

多任务 Dashboard 从同一 Release 的静态聚合结果中切换任务。仓库内当前定义
59 类眼底疾病与 DR 三阶段（Normal / NPDR / PDR）任务；后者不冒充不存在的
ICDR 五级标注。

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
