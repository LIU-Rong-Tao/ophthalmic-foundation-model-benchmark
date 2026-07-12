<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# VisionFM

## 模型概览

- **Model ID**：`visionfm`
- **模型类型**：多模态眼科基础模型
- **模态**：CFP, OCT, FFA, ultrasound, external_eye, slit_lamp, MRI, UBM
- **核心架构**：8个独立ViT-B/16编码器，每个模态一个编码器
- **预训练方式**：iBOT；masked image modeling + self-distillation
- **当前状态**：尚不可运行

## 官方入口

- 论文：[https://ai.nejm.org/doi/abs/10.1056/AIoa2300221](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221)
- 代码：[https://github.com/ABILab-CUHK/VisionFM](https://github.com/ABILab-CUHK/VisionFM)

## Checkpoint 资产

| Checkpoint | 模态 | 来源 | 访问条件 | 文件核验 | Adapter |
|---|---|---|---|---|---|
| `visionfm-external-eye` / External Eye | external_eye | [google_drive](https://drive.google.com/file/d/16zGHTD4ZcGAYW382kKHBw3TU6D1OtvTD/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-ffa` / FFA | FFA | [google_drive](https://drive.google.com/file/d/128izBUNV00Ojb9w9Dq3GhBvhWqzU-mla/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-fundus` / Fundus | CFP | [google_drive](https://drive.google.com/file/d/13uWm0a02dCWyARUcrCdHZIcEgRfBmVA4/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-mri` / MRI | MRI | [google_drive](https://drive.google.com/file/d/1fcfylnOWhfnZHBAKT9pQPufyS5ZYCXu0/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-oct` / OCT | OCT | [google_drive](https://drive.google.com/file/d/1o6E-ine2QLx2pxap-c77u-SU0FjxwypA/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-slit-lamp` / Slit Lamp | slit_lamp | [google_drive](https://drive.google.com/file/d/1pemWDkGoZYlqLQ6ooFINktyk8xnv9wY_/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-ubm` / UBM | UBM | [google_drive](https://drive.google.com/file/d/1q2fVOgFBnWNu1BsXaza1A-OIcCiifNUQ/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |
| `visionfm-ultrasound` / Ultrasound | ultrasound | [google_drive](https://drive.google.com/file/d/1IlD0snowxdEVvxmiIBZGR0D9uOcrCT2D/view?usp=sharing) | 登记为开放 | 待核验 | 未验证 |

## 输入与原生预处理

### `visionfm-external-eye`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-ffa`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-fundus`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-mri`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-oct`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-slit-lamp`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-ubm`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验
### `visionfm-ultrasound`
- 输入：待核验
- 归一化：待核验
- 预处理核验：待核验

## 特征输出

- `visionfm-external-eye`：embedding 维度 待核验
- `visionfm-ffa`：embedding 维度 待核验
- `visionfm-fundus`：embedding 维度 待核验
- `visionfm-mri`：embedding 维度 待核验
- `visionfm-oct`：embedding 维度 待核验
- `visionfm-slit-lamp`：embedding 维度 待核验
- `visionfm-ubm`：embedding 维度 待核验
- `visionfm-ultrasound`：embedding 维度 待核验

## 权重与许可限制

- 模型许可证：待核验
- 本仓库默认不重新分发第三方权重。
- Adapter smoke 不等于下游任务性能结论。

## 核验记录

| 核验项 | 状态 | 证据/记录 | 最近核验 |
|---|---|---|---|
| 论文 | 待核验 | https://ai.nejm.org/doi/abs/10.1056/AIoa2300221 | 尚未登记 |
| 官方代码 | 待核验 | https://github.com/ABILab-CUHK/VisionFM | 尚未登记 |
| Checkpoint 入口 | 待核验 | 8 个已登记入口 | 尚未登记 |
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
