<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# DERETFound

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

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `deretfound-pretraining` / Pretraining | CFP | [zenodo](https://zenodo.org/records/13340936/files/PreTraining.zip?download=1) | 登记为开放 | 待核验 | 未验证 |
| `deretfound-sd-retina` / Stable Diffusion Retina | CFP | [zenodo](https://zenodo.org/records/13340936/files/sd-retina-model.zip?download=1) | 登记为开放 | 待核验 | 未验证 |

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
| 论文 | 待核验 | https://www.nature.com/articles/s41551-025-01365-0 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/Jonlysun/DERETFound | 尚未登记 |
| Checkpoint 入口 | 待核验 | 2 个已登记入口 | 尚未登记 |
| Checkpoint 文件 | 待核验 | 尚未登记 | 尚未登记 |
| 许可证 | 待核验 | 尚未登记 | 尚未登记 |
| 原生预处理 | 待核验 | 尚未登记 | 尚未登记 |
| Adapter | 待核验 | not_started | 尚未登记 |
| 特征输出 | 待核验 | not_run | 尚未登记 |

## 待核验事项

- 论文
- 官方代码
- Checkpoint 入口
- Checkpoint 文件
- 许可证
- 原生预处理
- Adapter
- 特征输出

[返回 Model Zoo](../MODEL_ZOO.md)
