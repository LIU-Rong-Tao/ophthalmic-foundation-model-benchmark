<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# VisionUnite

## 模型概览

- **Model ID**：`visionunite`
- **模型类型**：眼科视觉-语言基础模型
- **模态**：CFP, OCT, FFA, MRI, CT, PET, X_ray, text
- **核心架构**：EVA-02/CLIP视觉编码器 + 体征分类Vision Adapter + Vision …
- **预训练方式**：两阶段训练：通用图文自回归生成预训练（仅LLM Loss）; MMFundus眼科指令微调（CLIP对比学习 + 特征分类 + 文本生成）。
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://ieeexplore.ieee.org/document/11124413](https://ieeexplore.ieee.org/document/11124413)
- 代码：[https://github.com/HUANGLIZI/VisionUnite](https://github.com/HUANGLIZI/VisionUnite)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `visionunite-default` / Default | CFP, OCT, FFA, MRI, CT, PET, X_ray, text | [google_drive](https://drive.google.com/file/d/1kbdpPklCdDxEgxcpsp4OgGjxvxKh5jpV/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `visionunite-default`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `visionunite-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://ieeexplore.ieee.org/document/11124413 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/HUANGLIZI/VisionUnite | 尚未登记 |
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
