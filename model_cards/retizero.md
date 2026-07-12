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

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `retizero-default` / Default | CFP, text | [google_drive](https://drive.google.com/file/d/14bMmnefO73_NL1Xc4x0A5qFNbuI7GqKM/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |

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
| 论文 | 待核验 | https://www.nature.com/articles/s41467-025-60577-9 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/LooKing9218/RetiZero | 尚未登记 |
| Checkpoint 入口 | 待核验 | 1 个已登记入口 | 尚未登记 |
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
