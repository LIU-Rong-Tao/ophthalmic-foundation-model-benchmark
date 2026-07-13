<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# VisionUnite

## 模型概览

- **Model ID**：`visionunite`
- **模型类型**：眼科视觉-语言基础模型
- **模态**：CFP, text
- **核心架构**：EVA-02/CLIP视觉编码器 + 体征分类Vision Adapter + Vision …
- **预训练方式**：两阶段训练：通用图文自回归生成预训练（仅LLM Loss）; MMFundus眼科指令微调（CLIP对比学习 + 特征分类 + 文本生成）。
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://ieeexplore.ieee.org/document/11124413](https://ieeexplore.ieee.org/document/11124413)
- 代码：[https://github.com/HUANGLIZI/VisionUnite](https://github.com/HUANGLIZI/VisionUnite)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `visionunite-default` / Default | multimodal_full_model | CFP, text | [google_drive](https://drive.google.com/file/d/1kbdpPklCdDxEgxcpsp4OgGjxvxKh5jpV/view?usp=sharing) | 登记为开放 | 已核验 | 未验证 |

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
| 论文 | 已核验 | https://ieeexplore.ieee.org/document/11124413 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/HUANGLIZI/VisionUnite | 2026-07-13 |
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
