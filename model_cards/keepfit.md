<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# KeepFIT

## 模型概览

- **Model ID**：`keepfit`
- **模型类型**：视觉-语言眼科基础模型
- **模态**：CFP, OCT, text
- **核心架构**：ResNet-50图像编码器 + BioClinicalBERT文本编码器 + 视觉文本投影头…
- **预训练方式**：知识增强图文对比预训练
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67)
- 代码：[https://github.com/lxirich/MM-Retinal](https://github.com/lxirich/MM-Retinal)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `keepfit-ffa-ir-mmretinal-ffa` / FFA-IR + MM-Retinal FFA | FFA | [google_drive](https://drive.google.com/file/d/1fdCRDbKJKZcqBlmdEdETygZ8EsBu5QlV/view) | 登记为开放 | 待核验 | 未验证 |
| `keepfit-flair-mmretinal-cfp` / FLAIR + MM-Retinal CFP | CFP | [google_drive](https://drive.google.com/file/d/1w6poCkZeqSTHsLYz1R9-z5Ttc0Vw0qSw/view) | 登记为开放 | 待核验 | 未验证 |
| `keepfit-half-flair-mmretinal-cfp` / Half FLAIR + MM-Retinal CFP | CFP | [google_drive](https://drive.google.com/file/d/1o4EDSifmcN7cKDP5w5qvS_wWiyfEZ6UN/view) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `keepfit-ffa-ir-mmretinal-ffa`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `keepfit-flair-mmretinal-cfp`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `keepfit-half-flair-mmretinal-cfp`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `keepfit-ffa-ir-mmretinal-ffa`：embedding 维度 待核验
- `keepfit-flair-mmretinal-cfp`：embedding 维度 待核验
- `keepfit-half-flair-mmretinal-cfp`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/lxirich/MM-Retinal | 尚未登记 |
| Checkpoint 入口 | 待核验 | 3 个已登记入口 | 尚未登记 |
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
