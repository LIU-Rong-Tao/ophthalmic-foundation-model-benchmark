<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# RETFound-DE

## 模型概览

- **Model ID**：`deretfound`
- **模型类型**：眼科视觉基础模型
- **模态**：CFP
- **核心架构**：ViT-L/16 MAE编码器 + ViT-S解码器
- **预训练方式**：两阶段MAE：合成CFP MAE预训练 + 真实CFP MAE领域适配
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://www.nature.com/articles/s41551-025-01365-0](https://www.nature.com/articles/s41551-025-01365-0)
- 代码：[https://github.com/Jonlysun/DERETFound](https://github.com/Jonlysun/DERETFound)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `deretfound-pretraining` / Pretraining | foundation_encoder | CFP | [zenodo](https://zenodo.org/records/13340936/files/PreTraining.zip?download=1) | 登记为开放 | 已核验 | 未验证 |
| `deretfound-sd-retina` / Stable Diffusion Retina | generative_model | CFP | [zenodo](https://zenodo.org/records/13340936/files/sd-retina-model.zip?download=1) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `deretfound-pretraining`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `deretfound-sd-retina`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `deretfound-pretraining`：embedding 维度 待核验
- `deretfound-sd-retina`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://www.nature.com/articles/s41551-025-01365-0 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/Jonlysun/DERETFound | 2026-07-13 |
| Checkpoint 入口 | 已核验 | 2 个已登记入口 | 2026-07-13 |
| 官方 Checkpoint 文件 | 已核验 | 2 个官方文件已完成入口/实际文件探测；本地 SHA256 见 download_manifest.csv | 2026-07-13 |
| 许可证 | 待核验 | 尚未登记 | 2026-07-13 |
| 原生预处理 | 待核验 | 尚未登记 | 2026-07-13 |
| Adapter | 待核验 | not_started | 2026-07-13 |
| 特征输出 | 待核验 | not_run | 2026-07-13 |

## 待核验事项

- 许可证
- 原生预处理
- Adapter
- 特征输出

[返回 Model Zoo](../MODEL_ZOO.md)
