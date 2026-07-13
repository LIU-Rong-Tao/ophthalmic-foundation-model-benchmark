<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# RETFound

## 模型概览

- **Model ID**：`retfound`
- **模型类型**：眼科视觉基础模型
- **模态**：CFP, OCT
- **核心架构**：ViT-Large/16 / masked_autoencoding
- **预训练方式**：MAE；随机遮挡patch后重建像素
- **当前状态**：可提取特征

## 官方入口

- 论文：[https://www.nature.com/articles/s41586-023-06555-x](https://www.nature.com/articles/s41586-023-06555-x)
- 代码：[https://github.com/rmaphoh/RETFound](https://github.com/rmaphoh/RETFound)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `retfound-cfp` / CFP | foundation_encoder | CFP | [huggingface](https://huggingface.co/YukunZhou/RETFound_mae_natureCFP) | 需认证/申请 | 已核验 | 已验证 |
| `retfound-oct` / OCT | foundation_encoder | OCT | [huggingface](https://huggingface.co/YukunZhou/RETFound_mae_natureOCT) | 需认证/申请 | 已核验 | 未验证 |

## 输入与原生预处理

### `retfound-cfp`
- 输入：RGB，256 × 256
- Resize：256 × 256，bicubic
- Crop：center，256 × 256
- 归一化：ImageNet mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225)
- 预处理核验：待核验
### `retfound-oct`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `retfound-cfp`：embedding 维度 1024
- `retfound-oct`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://www.nature.com/articles/s41586-023-06555-x | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/rmaphoh/RETFound | 2026-07-13 |
| Checkpoint 入口 | 已核验 | 2 个已登记入口 | 2026-07-13 |
| 官方 Checkpoint 文件 | 已核验 | 2 个官方文件已完成入口/实际文件探测；本地 SHA256 见 download_manifest.csv | 2026-07-13 |
| 许可证 | 待核验 | 尚未登记 | 2026-07-13 |
| 原生预处理 | 待核验 | official_code_and_adapter_smoke | 2026-07-13 |
| Adapter | 已核验 | implemented | 2026-07-13 |
| 特征输出 | 已核验 | passed | 2026-07-13 |

## 待核验事项

- 许可证
- 原生预处理

[返回 Model Zoo](../MODEL_ZOO.md)
