<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# EyeCLIP

## 模型概览

- **Model ID**：`eyeclip`
- **模型类型**：视觉-语言眼科基础模型
- **模态**：CFP, OCT, FFA, ICGA, FAF, ultrasound, external_eye, slit_lamp, specular_microscopy, corneal_photography, RetCam, text
- **核心架构**：ViT-B/32 / image-image and image-text contrastive learning
- **预训练方式**：联合训练：MIM + image-image contrastive learning + image-text contrastive learning
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://www.nature.com/articles/s41746-025-01772-2](https://www.nature.com/articles/s41746-025-01772-2)
- 代码：[https://github.com/Michi-3000/EyeCLIP](https://github.com/Michi-3000/EyeCLIP)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `eyeclip-default` / Default | vision_language_model | CFP, OCT, FFA, ICGA, FAF, ultrasound, external_eye, slit_lamp, specular_microscopy, corneal_photography, RetCam, text | [google_drive](https://drive.google.com/file/d/1kWpbDqFCFt4j8RkYqacV4nl-aCKZfqZr/view?usp=sharing) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `eyeclip-default`
- 输入：RGB，224 × 224
- 归一化：CLIP mean=(0.48145466,0.4578275,0.40821073), std=(0.26862954,0.26130258,0.27577711)
- 预处理核验：已核验

## 特征输出

- `eyeclip-default`：embedding 维度 512

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://www.nature.com/articles/s41746-025-01772-2 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/Michi-3000/EyeCLIP | 2026-07-13 |
| Checkpoint 入口 | 已核验 | 1 个已登记入口 | 2026-07-13 |
| 官方 Checkpoint 文件 | 已核验 | 1 个官方文件已完成入口/实际文件探测；本地 SHA256 见 download_manifest.csv | 2026-07-13 |
| 许可证 | 待核验 | 尚未登记 | 2026-07-13 |
| 原生预处理 | 已核验 | 尚未登记 | 2026-07-13 |
| Adapter | 待核验 | not_started | 2026-07-13 |
| 特征输出 | 待核验 | not_run | 2026-07-13 |

## 待核验事项

- 许可证
- Adapter
- 特征输出

[返回 Model Zoo](../MODEL_ZOO.md)
