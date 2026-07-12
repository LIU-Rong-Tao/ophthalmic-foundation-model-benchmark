# OphBench

**OphBench（Ophthalmic Foundation Model Benchmark）** 是面向眼科基础模型的开放注册、统一接入与可复现评测工具包。

[模型目录](MODEL_ZOO.md) · [快速开始](docs/quickstart.md) · [评测协议](docs/evaluation_tracks.md) · [新增模型](docs/adding_a_model.md) · [权重政策](docs/weight_policy.md)

> 当前版本为 **v0.2 release candidate**。注册表包含 15 个模型、27 个 checkpoint；其中只有 RETFound CFP 已完成真实 Adapter 与 smoke 验证。其余条目主要用于资产审核与后续接入，不代表可以直接运行。

## 关键能力

- **统一模型注册表**：一个模型、一个 checkpoint 对应独立 YAML，自动校验并生成 Markdown、CSV、JSON 目录。
- **统一图像编码接口**：模型原生预处理、checkpoint 显式传入、固定维度 embedding 输出。
- **Frozen Feature Transfer v0.1**：冻结编码器，使用相同数据划分和 Logistic Regression 探针评估迁移能力。
- **可追踪运行产物**：保存有效配置、split fingerprint、预测、指标、bootstrap 置信区间与环境信息。
- **安全权重边界**：不重新分发第三方权重，不自动绕过 gated/authenticated 访问。
- **科研声明隔离**：论文报告结果、协议 pilot 与本项目复现结果严格区分。

## 安装

基础注册表工具支持 Python 3.10 或 3.11：

```bash
git clone https://github.com/LIU-Rong-Tao/ophthalmic-foundation-model-benchmark.git
cd ophthalmic-foundation-model-benchmark
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell 激活命令为 `.\.venv\Scripts\Activate.ps1`。

运行 RETFound 或冻结特征评测时再安装可选依赖：

```bash
pip install -e ".[retfound,frozen-transfer]"
```

## 五分钟快速检查

```bash
ophbench registry validate
ophbench catalog build --check
ophbench list-models
ophbench show-model retfound
ophbench doctor --model retfound
```

`doctor` 只检查登记状态、Adapter 状态和权重访问条件，不会下载权重。

## 当前工作流

```text
模型/Checkpoint 注册
        ↓
权重、许可证与预处理审核
        ↓
统一 Adapter：load → preprocess → encode_image
        ↓
冻结 embedding
        ↓
train 拟合探针 → val 选择超参数 → test 评测一次
        ↓
预测、指标、置信区间与可追踪 manifest
```

当前 pilot 配置：

```bash
python scripts/run_frozen_feature_transfer.py \
  --protocol protocols/frozen_feature_transfer_v0_1.yaml \
  --data-root /path/to/APTOS2019 \
  --checkpoint-path /path/to/RETFound_mae_natureCFP.pth \
  --output-dir outputs/retfound-aptos-pilot \
  --device cuda:0
```

该 pilot 的角色是 `pilot_protocol_validation`，不能用于宣称模型优劣或患者级泛化。

## 支持矩阵

| 层级 | 当前状态 | 含义 |
|---|---:|---|
| 已验证可运行 | RETFound CFP | Adapter 已实现并通过 smoke，可提取 1024 维 CFP embedding |
| 协议 pilot | RETFound CFP + APTOS2019 | Frozen Feature Transfer v0.1 可复现性验证，不是正式模型比较 |
| Adapter 开发中 | 0 | 尚未批准第二个模型实现 |
| 仅元数据登记 | 14 个模型 | 尚未完成权重、许可证、预处理与运行核验 |

完整登记信息见 [MODEL_ZOO.md](MODEL_ZOO.md)。登记数量不等于支持数量。

## 标准输出

一次 Frozen Feature Transfer pilot 会生成：

```text
run/
├── protocol.yaml
├── effective_config.yaml
├── split_manifest.csv
├── split_manifest.json
├── run_manifest.json
├── validation_results.csv
├── selected_probe.json
├── test_predictions.csv
├── metrics.json
├── bootstrap_summary.csv
├── confusion_matrix.csv
└── artifact_manifest.json
```

数据、权重、embedding 和运行输出默认不提交到 Git。

## 文档

- [安装与环境](docs/installation.md)
- [快速开始](docs/quickstart.md)
- [模型 Adapter](docs/model_adapters.md)
- [数据集约定](docs/datasets.md)
- [评测 Track](docs/evaluation_tracks.md)
- [输出与复现](docs/outputs.md)
- [新增模型](docs/adding_a_model.md)
- [常见问题](docs/faq.md)

## 项目边界

OphBench 不是权重镜像，也不是医疗诊断系统。它提供研究评测基础设施，不提供诊断建议，不默认重新分发模型权重或医学数据。

## 致谢

仓库组织与工具包体验参考了 [Mahmood Lab TRIDENT](https://github.com/mahmoodlab/TRIDENT) 的一体化流程、doctor 预检、模型工厂、可选依赖、可恢复运行和文档分层思想；OphBench 面向眼科图像与下游迁移评测，不复制 TRIDENT 的 WSI 处理实现。

## 许可证与引用

仓库代码许可证见 [LICENSE](LICENSE)。使用第三方模型时还必须遵守对应模型与数据集许可证。正式论文引用信息尚未发布；当前可引用本仓库 URL 与具体 commit/tag。
