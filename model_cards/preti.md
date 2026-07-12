<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# PRETI

## 模型概览

- **Model ID**：`preti`
- **模型类型**：眼科视觉基础模型
- **模态**：CFP
- **核心架构**：ViT-S或ViT-B编码器 + ViT-S解码器 + Learnable Metadata …
- **预训练方式**：患者级图像对重建 + 视网膜区域自适应掩码 + 元数据引导联合学习
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50](https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50)
- 代码：[https://github.com/MICV-yonsei/PRETI](https://github.com/MICV-yonsei/PRETI)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `preti-default` / Default | CFP | [google_drive](https://drive.google.com/file/d/1mEFm3bxSPPOm4bLPC9Ey64oeq-6F0S0G/view?usp=drive_link) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `preti-default`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `preti-default`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/MICV-yonsei/PRETI | 尚未登记 |
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
