<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# MIRAGE

## 模型概览

- **Model ID**：`mirage`
- **模型类型**：多模态眼科视觉基础模型
- **模态**：OCT, SLO, retinal_layer_pseudolabels
- **核心架构**：MultiMAE式多模态掩码自编码器：共享ViT编码器 + 模态特异性线性投影层 + 模态特异…
- **预训练方式**：MultiMAE多模态自监督掩码重建预训练
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://www.nature.com/articles/s41746-025-01852-3](https://www.nature.com/articles/s41746-025-01852-3)
- 代码：[https://github.com/j-morano/MIRAGE](https://github.com/j-morano/MIRAGE)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `mirage-base` / Base | OCT, SLO | [huggingface](https://huggingface.co/j-morano/MIRAGE-Base) | 登记为开放 | 待核验 | 未验证 |
| `mirage-large` / Large | OCT, SLO | [huggingface](https://huggingface.co/j-morano/MIRAGE-Large) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `mirage-base`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `mirage-large`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `mirage-base`：embedding 维度 待核验
- `mirage-large`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://www.nature.com/articles/s41746-025-01852-3 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/j-morano/MIRAGE | 尚未登记 |
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
