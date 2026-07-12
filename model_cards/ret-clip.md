<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# RET-CLIP

## 模型概览

- **Model ID**：`ret-clip`
- **模型类型**：视觉-语言眼科基础模型
- **模态**：CFP, text
- **核心架构**：ViT-B/16视觉编码器 + RoBERTa-Base中文文本编码器 + MLP
- **预训练方式**：左眼、右眼、患者三级图文对比预训练
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://doi.org/10.1007/978-3-031-72390-2_66](https://doi.org/10.1007/978-3-031-72390-2_66)
- 代码：[https://github.com/sStonemason/RET-CLIP](https://github.com/sStonemason/RET-CLIP)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `ret-clip-default` / Default | CFP, text | [google_drive](https://drive.google.com/file/d/1lYrAg5qzFbNghEW-3UB36v9WL-mo5eN9/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `ret-clip-default`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `ret-clip-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://doi.org/10.1007/978-3-031-72390-2_66 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/sStonemason/RET-CLIP | 尚未登记 |
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
