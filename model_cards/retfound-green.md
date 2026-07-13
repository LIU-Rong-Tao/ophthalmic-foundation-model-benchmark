<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# RETFound-Green

## 模型概览

- **Model ID**：`retfound-green`
- **模型类型**：眼科视觉基础模型
- **模态**：CFP
- **核心架构**：ViT-Small + 4个Register Tokens
- **预训练方式**：Self-supervised Token Reconstruction；学生模型从强扰动输入预测教师token特征
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://www.nature.com/articles/s41467-025-62123-z](https://www.nature.com/articles/s41467-025-62123-z)
- 代码：[https://github.com/justinengelmann/RETFound_Green](https://github.com/justinengelmann/RETFound_Green)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `retfound-green-v0.1` / v0.1 | foundation_encoder | CFP | [github_release](https://github.com/justinengelmann/RETFound_Green/releases/tag/v0.1) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `retfound-green-v0.1`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `retfound-green-v0.1`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://www.nature.com/articles/s41467-025-62123-z | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/justinengelmann/RETFound_Green | 2026-07-13 |
| Checkpoint 入口 | 已核验 | 1 个已登记入口 | 2026-07-13 |
| 官方 Checkpoint 文件 | 已核验 | 1 个官方文件已完成入口/实际文件探测；本地 SHA256 见 download_manifest.csv | 2026-07-13 |
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
