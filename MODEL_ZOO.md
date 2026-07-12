<!-- AUTO-GENERATED. DO NOT EDIT MANUALLY. -->
# 眼科基础模型目录

Models: **15**  
Checkpoints: **27**

本页展示模型资产的收录与核验进度。**已收录不等于已支持运行**。

## 核验概览

- 部分已核验：1 个模型
- 待核验：14 个模型


## CFP 模型

| 模型 | 模态 | 核心架构 | Checkpoint | 权重访问 | 核验状态 | 运行状态 |
|---|---|---|---:|---|---|---|
| [DERETFound](model_cards/deretfound.md) | CFP | ViT-L/16 MAE编码器 + ViT-S解码器 | 2 | 登记为开放 | 待核验 | 尚不可运行 |
| [PRETI](model_cards/preti.md) | CFP | ViT-S或ViT-B编码器 + ViT-S解码器 + Learnable Metadata … | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [RETFound-Green](model_cards/retfound-green.md) | CFP | ViT-Small + 4个Register Tokens | 1 | 登记为开放 | 待核验 | 尚不可运行 |

## OCT 模型

| 模型 | 模态 | 核心架构 | Checkpoint | 权重访问 | 核验状态 | 运行状态 |
|---|---|---|---:|---|---|---|
| [FMUE](model_cards/fmue.md) | OCT | RETFound ViT-Large/16编码器 + LoRA + 基于证据学习的Dirich… | 1 | 登记为开放 | 待核验 | 尚不可运行 |

## 多模态眼科模型

| 模型 | 模态 | 核心架构 | Checkpoint | 权重访问 | 核验状态 | 运行状态 |
|---|---|---|---:|---|---|---|
| [MIRAGE](model_cards/mirage.md) | OCT, SLO, retinal_layer_pseudolabels | MultiMAE式多模态掩码自编码器：共享ViT编码器 + 模态特异性线性投影层 + 模态特异… | 2 | 登记为开放 | 待核验 | 尚不可运行 |
| [RETFound](model_cards/retfound.md) | CFP, OCT | ViT-Large/16 / masked_autoencoding | 2 | 需认证/申请 | 部分已核验 | 可提取特征 |
| [VisionFM](model_cards/visionfm.md) | CFP, OCT, FFA, ultrasound, external_eye, slit_lamp, MRI, UBM | 8个独立ViT-B/16编码器，每个模态一个编码器 | 8 | 登记为开放 | 待核验 | 尚不可运行 |

## 视觉语言模型

| 模型 | 模态 | 核心架构 | Checkpoint | 权重访问 | 核验状态 | 运行状态 |
|---|---|---|---:|---|---|---|
| [EyeCLIP](model_cards/eyeclip.md) | CFP, OCT, FFA, ICGA, FAF, ultrasound, external_eye, slit_lamp, specular_microscopy, CT, RetCam, text | ViT-Large/16图像编码器 + 文本编码器 | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [FLAIR](model_cards/flair.md) | CFP, text | ResNet-50图像编码器 + BioClinicalBERT文本编码器 | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [KeepFIT](model_cards/keepfit.md) | CFP, OCT, text | ResNet-50图像编码器 + BioClinicalBERT文本编码器 + 视觉文本投影头… | 3 | 登记为开放 | 待核验 | 尚不可运行 |
| [RET-CLIP](model_cards/ret-clip.md) | CFP, text | ViT-B/16视觉编码器 + RoBERTa-Base中文文本编码器 + MLP | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [RetiZero](model_cards/retizero.md) | CFP, text | 冻结的 RETFound 图像编码器ViT-Large/16 ＋ BioClinicalBER… | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [UrFound](model_cards/urfound.md) | CFP, OCT, text | 共享ViT-B编码器 + 8层图像解码器 + 6层条件语言解码器 | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [ViLReF](model_cards/vilref.md) | CFP, text | ViT-B/16图像编码器 + RoBERTa-wwm-ext-base-chinese文本编… | 1 | 登记为开放 | 待核验 | 尚不可运行 |
| [VisionUnite](model_cards/visionunite.md) | CFP, OCT, FFA, MRI, CT, PET, X_ray, text | EVA-02/CLIP视觉编码器 + 体征分类Vision Adapter + Vision … | 1 | 登记为开放 | 待核验 | 尚不可运行 |

## 说明

- 待核验记录不能视为官方确认信息。
- “登记为开放”只表示 seed 中的访问记录，不代表权重和许可证已核验。
- 本仓库默认不重新分发第三方权重。
- 论文报告结果不等于本项目复现结果。
