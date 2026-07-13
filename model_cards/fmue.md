<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# FMUE

## 模型概览

- **Model ID**：`fmue`
- **模型类型**：OCT 不确定性分类模型（公开权重为任务 checkpoint）
- **模态**：OCT
- **核心架构**：ViT-Large/16 + 16 类 OCT 分类头（Dirichlet evidence …
- **预训练方式**：冻结RETFound-OCT主干，通过LoRA进行参数高效监督微调，并使用显式疾病标签训练Dirichlet证据分类器；在验证集上确定不确定性阈值，将高不确定性样本转交医生复核。
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://doi.org/10.1016/j.xcrm.2024.101876](https://doi.org/10.1016/j.xcrm.2024.101876)
- 代码：[https://github.com/yuanyuanpeng0129/FMUE](https://github.com/yuanyuanpeng0129/FMUE)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `fmue-default` / Official 16-class OCT classifier | task_checkpoint | OCT | [google_drive](https://drive.google.com/file/d/1-rdx6VPJNWVwkjamkplEoyUOHNGweUho/view?usp=sharing) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `fmue-default`
- 输入：RGB，224 × 224
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `fmue-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://doi.org/10.1016/j.xcrm.2024.101876 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/yuanyuanpeng0129/FMUE | 2026-07-13 |
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
