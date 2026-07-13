<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# UrFound

## 模型概览

- **Model ID**：`urfound`
- **模型类型**：视觉-语言眼科基础模型
- **模态**：CFP, OCT, text
- **核心架构**：共享ViT-B编码器 + 8层图像解码器 + 6层条件语言解码器
- **预训练方式**：图像掩码重建MIM + 图像条件掩码语言建模MLM
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70](https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70)
- 代码：[https://github.com/yukkai/UrFound](https://github.com/yukkai/UrFound)

## Checkpoint 资产

| Checkpoint | 资产类型 | 模态 | 来源 | 访问条件 | 官方文件探测 | Adapter |
|---|---|---|---|---|---|---|
| `urfound-default` / Default | vision_language_model | CFP, OCT, text | [huggingface](https://huggingface.co/yyyyk/UrFound) | 登记为开放 | 已核验 | 未验证 |

## 输入与原生预处理

### `urfound-default`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `urfound-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 已核验 | https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70 | 2026-07-13 |
| 官方代码 | 已核验 | https://github.com/yukkai/UrFound | 2026-07-13 |
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
