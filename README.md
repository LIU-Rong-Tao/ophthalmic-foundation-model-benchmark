# OphBench：眼科基础模型资源库

OphBench 当前用于**收集、核验和规范登记眼科基础模型资产**，让研究团队能够快速找到模型的论文、官方代码、输入模态、checkpoint、权重获取条件和接入状态。

当前收录 **15 个模型、27 个 checkpoint**。收录不等于已经支持运行；只有明确标记为 Adapter 已实现的模型才具备本仓库验证过的调用能力。

[模型目录](MODEL_ZOO.md) · [收集规范](docs/model_collection.md) · [核验状态](docs/verification_status.md) · [新增模型](docs/adding_a_model.md) · [权重政策](docs/weight_policy.md)


## 快速入口

- [模型与权重目录](docs/MODEL_WEIGHT_CATALOG.md)
- [下载与文件核验](docs/DOWNLOAD_AND_VERIFY.md)
- [机器可读下载清单](catalog/download_manifest.csv)
- [下一阶段评估交接](docs/EVALUATION_HANDOFF.md)

本仓库当前第一版完成的是眼科基础模型的收集、官方来源核验、权重获取信息和后续评估交接，不声称已经完成统一性能评测。当前服务器侧已有 19 个 checkpoint 通过文件大小、SHA256 和非 HTML 校验；8 个 VisionFM checkpoint 因属于项目初代模型而不重复获取。权重文件不提交到 Git。

## 当前主线

```text
公开模型收集
→ 核验论文、官方代码、权重和模态
→ 形成统一模型与 checkpoint 登记
→ 为后续团队评测和 OphAgent 接入提供模型资产
```

当前不建设完整训练平台、完整 Benchmark 平台或大规模特征提取系统。

## 模型状态怎么看

Model Zoo 使用五个直观状态：

- **已收录**：已有结构化模型和 checkpoint 记录；
- **信息核验**：论文、代码及核心模型信息的核验进度；
- **权重核验**：下载入口、访问条件和本地文件是否核验；
- **Adapter**：是否已实现本仓库统一接口；
- **特征提取**：是否通过真实 checkpoint 的编码 smoke。

目前 RETFound CFP 是首个 Adapter 已实现并通过特征编码 smoke 的接入示例，其余模型仍以收集和核验为主。

## 查看和维护资源库

```bash
pip install -e ".[dev]"
ophbench registry validate
ophbench catalog build --check
ophbench list-models
ophbench show-model retfound
```

YAML 是唯一权威数据源；`MODEL_ZOO.md` 和 `catalog/` 自动生成，不应手工修改。

## 增加一个模型

提交内容包括：

1. `registry/models/<model_id>.yaml` 模型元数据；
2. `registry/checkpoints/<checkpoint_id>.yaml` checkpoint 元数据；
3. 支撑论文、官方代码、权重、许可证和预处理结论的官方链接；
4. 无法核验的字段保持待核验，不凭推测补全；
5. Adapter 是可选项，不要求每个收录模型立即实现。

可复制 [模型模板](templates/model.yaml) 和 [Checkpoint 模板](templates/checkpoint.yaml)，详细规则见 [新增模型](docs/adding_a_model.md) 与 [贡献指南](CONTRIBUTING.md)。

## 已有实验性示例

- **RETFound CFP Adapter**：第一个统一图像编码接口示例；权重需由使用者从官方来源取得，本仓库不重新分发。
- **Frozen Feature Transfer pilot**：说明标准 embedding 可以用于后续评测，仅是可行性示例，不是当前仓库主线，也不构成模型优劣结论。

## 后续方向

统一加载、模型原生预处理和统一特征提取是后续扩展方向。只有团队确认需要评测某个模型时，才逐个核验并实现 Adapter；当前只保留轻量接口与数据契约，不全面建设运行系统。

详见 [项目范围](docs/project_scope.md) 和 [路线图](docs/roadmap.md)。

## 安全与边界

- 不提交第三方模型权重、医学数据、访问令牌或私有下载链接；
- 不绕过 gated/authenticated 权重访问条件；
- 论文报告结果不等于本项目复现结果；
- 本仓库用于研究资源整理，不提供医疗诊断建议。

仓库组织参考 [Mahmood Lab TRIDENT](https://github.com/mahmoodlab/TRIDENT) 的清晰首页、模型目录、模型接入说明和可扩展接口思想；当前不复制其完整运行、缓存或多 GPU 系统。
