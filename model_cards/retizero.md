<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# RetiZero

## 模型概览

- **Model ID**：`retizero`
- **模型类型**：视觉-语言眼科基础模型
- **模态**：CFP, text
- **核心架构**：冻结的 RETFound 图像编码器ViT-Large/16 ＋ BioClinicalBER…
- **预训练方式**：CLIP风格图文对比学习
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://www.nature.com/articles/s41467-025-60577-9](https://www.nature.com/articles/s41467-025-60577-9)
- 代码：[https://github.com/LooKing9218/RetiZero](https://github.com/LooKing9218/RetiZero)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `retizero-default` / Default | vision_language_model | CFP, text | [google_drive](https://drive.google.com/file/d/14bMmnefO73_NL1Xc4x0A5qFNbuI7GqKM/view?usp=sharing) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `retizero-default`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `retizero-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://www.nature.com/articles/s41467-025-60577-9 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/LooKing9218/RetiZero | 2026-07-13 |
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
