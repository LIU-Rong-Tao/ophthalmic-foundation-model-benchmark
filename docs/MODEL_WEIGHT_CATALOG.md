# 眼科基础模型权重总目录

本目录覆盖 OphBench 第一版收录的 15 个模型和 27 个 checkpoint。它记录官方来源、文件信息、访问条件与当前资产状态，不表示已完成统一性能评测。

> SHA256 用于确认重新下载的文件与本项目已核验文件逐字节一致；它用于完整性和版本核验，但不能单独证明下载来源是官方的。官方来源由论文、官方代码仓库和官方权重页面共同证明。

## 完整总表

期刊影响因子只作为论文发表平台的参考信息，不代表模型性能、适配性或复现质量。数值标注年份并链接期刊/学会官方来源；会议与预印本记为不适用，无法从官方来源确认的记为尚未核验。

| 模型名称 | Checkpoint | 输入模态 | 论文/期刊 | 影响因子 | 权重文件 | 文件大小 | 官方权重页面 | 官方代码 | 获取方式 | 使用限制 | 当前状态 |
|---|---|---|---|---|---|---:|---|---|---|---|---|
| DERETFound | deretfound-pretraining | CFP | [论文](https://www.nature.com/articles/s41551-025-01365-0) · Nature Biomedical Engineering | [26.3（2025）](https://www.nature.com/natbiomedeng/journal-impact) | PreTraining.zip | 3.66 GB | [官方权重](https://zenodo.org/records/13340936/files/PreTraining.zip) | [官方代码](https://github.com/Jonlysun/DERETFound) | 从官方 zenodo 页面下载 | 代码仓库存在许可证，但权重是否适用同一许可尚未明确。 | 已下载并核验 |
| DERETFound | deretfound-sd-retina | CFP | [论文](https://www.nature.com/articles/s41551-025-01365-0) · Nature Biomedical Engineering | [26.3（2025）](https://www.nature.com/natbiomedeng/journal-impact) | sd-retina-model.zip | 3.19 GB | [官方权重](https://zenodo.org/records/13340936/files/sd-retina-model.zip) | [官方代码](https://github.com/Jonlysun/DERETFound) | 从官方 zenodo 页面下载 | 代码仓库存在许可证，但权重是否适用同一许可尚未明确。 | 已下载并核验 |
| EyeCLIP | eyeclip-default | CFP;OCT;FFA;ICGA;FAF;ultrasound;external_eye;slit_lamp;specular_microscopy;CT;RetCam;text | [论文](https://www.nature.com/articles/s41746-025-01772-2) · NPJ Digital Medicine | [18.0（2025）](https://www.nature.com/npjdigitalmed/journal-impact) | eyeclip.pt | 2.14 GB | [官方权重](https://drive.google.com/file/d/1kWpbDqFCFt4j8RkYqacV4nl-aCKZfqZr/view) | [官方代码](https://github.com/Michi-3000/EyeCLIP) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| FLAIR | flair-default | CFP;text | [论文](https://doi.org/10.1016/j.media.2024.103357) · Medical Image Analysis | 尚未核验 | model.safetensors | 533.32 MB | [官方权重](https://huggingface.co/jusiro2/FLAIR) | [官方代码](https://github.com/jusiro/FLAIR) | 从官方 huggingface 页面下载 | 官方声明代码与权重采用 Apache-2.0；使用前仍应保留许可与来源说明。 | 已下载并核验 |
| FMUE | fmue-default | OCT | [论文](https://doi.org/10.1016/j.xcrm.2024.101876) · Cell Reports Medicine | 尚未核验 | FMUE.pth | 1.22 GB | [官方权重](https://drive.google.com/file/d/1-rdx6VPJNWVwkjamkplEoyUOHNGweUho/view) | [官方代码](https://github.com/yuanyuanpeng0129/FMUE) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| KeepFIT | keepfit-ffa-ir-mmretinal-ffa | FFA | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67) · MICCAI | 不适用 | KeepFIT (FFA-IR+MM).pth | 537.66 MB | [官方权重](https://drive.google.com/file/d/1fdCRDbKJKZcqBlmdEdETygZ8EsBu5QlV/view) | [官方代码](https://github.com/lxirich/MM-Retinal) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| KeepFIT | keepfit-flair-mmretinal-cfp | CFP | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67) · MICCAI | 不适用 | KeepFIT (flair+MM).pth | 537.66 MB | [官方权重](https://drive.google.com/file/d/1w6poCkZeqSTHsLYz1R9-z5Ttc0Vw0qSw/view) | [官方代码](https://github.com/lxirich/MM-Retinal) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| KeepFIT | keepfit-half-flair-mmretinal-cfp | CFP | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67) · MICCAI | 不适用 | KeepFIT (50%flair+MM).pth | 537.66 MB | [官方权重](https://drive.google.com/file/d/1o4EDSifmcN7cKDP5w5qvS_wWiyfEZ6UN/view) | [官方代码](https://github.com/lxirich/MM-Retinal) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| MIRAGE | mirage-base | OCT;SLO | [论文](https://www.nature.com/articles/s41746-025-01852-3) · npj Digital Medicine | [18.0（2025）](https://www.nature.com/npjdigitalmed/journal-impact) | model.safetensors | 348.11 MB | [官方权重](https://huggingface.co/j-morano/MIRAGE-Base) | [官方代码](https://github.com/j-morano/MIRAGE) | 从官方 huggingface 页面下载 | 官方声明模型与代码采用 CC BY 4.0，使用时需署名。 | 已下载并核验 |
| MIRAGE | mirage-large | OCT;SLO | [论文](https://www.nature.com/articles/s41746-025-01852-3) · npj Digital Medicine | [18.0（2025）](https://www.nature.com/npjdigitalmed/journal-impact) | model.safetensors | 1.22 GB | [官方权重](https://huggingface.co/j-morano/MIRAGE-Large) | [官方代码](https://github.com/j-morano/MIRAGE) | 从官方 huggingface 页面下载 | 官方声明模型与代码采用 CC BY 4.0，使用时需署名。 | 已下载并核验 |
| PRETI | preti-default | CFP | [论文](https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50) · MICCAI | 不适用 | checkpoint-119.pth | 1.12 GB | [官方权重](https://drive.google.com/file/d/1mEFm3bxSPPOm4bLPC9Ey64oeq-6F0S0G/view) | [官方代码](https://github.com/MICV-yonsei/PRETI) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| RET-CLIP | ret-clip-default | CFP;text | [论文](https://doi.org/10.1007/978-3-031-72390-2_66) · MICCAI | 不适用 | ret-clip.pt | 767.61 MB | [官方权重](https://drive.google.com/file/d/1lYrAg5qzFbNghEW-3UB36v9WL-mo5eN9/view) | [官方代码](https://github.com/sStonemason/RET-CLIP) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| RETFound | retfound-cfp | CFP | [论文](https://www.nature.com/articles/s41586-023-06555-x) · Nature | [56.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics) | RETFound_mae_natureCFP.pth | 3.95 GB | [官方权重](https://huggingface.co/YukunZhou/RETFound_mae_natureCFP) | [官方代码](https://github.com/rmaphoh/RETFound) | 在官方 Hugging Face 页面申请权限并使用本人账号下载 | 需接受官方权重访问条款；不得推断允许再分发。 | 已下载并核验；后续使用者仍需自行申请官方 Hugging Face 访问权限。 |
| RETFound-Green | retfound-green-v0.1 | CFP | [论文](https://www.nature.com/articles/s41467-025-62123-z) · Nature Communications | [18.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics) | retfoundgreen_statedict.pth | 87.40 MB | [官方权重](https://github.com/justinengelmann/RETFound_Green/releases/tag/v0.1) | [官方代码](https://github.com/justinengelmann/RETFound_Green) | 从官方 github_release 页面下载 | 仅限非商业研究用途；不得推断允许再分发。 | 已下载并核验 |
| RETFound | retfound-oct | OCT | [论文](https://www.nature.com/articles/s41586-023-06555-x) · Nature | [56.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics) | RETFound_mae_natureOCT.pth | 3.95 GB | [官方权重](https://huggingface.co/YukunZhou/RETFound_mae_natureOCT) | [官方代码](https://github.com/rmaphoh/RETFound) | 在官方 Hugging Face 页面申请权限并使用本人账号下载 | 需接受官方权重访问条款；不得推断允许再分发。 | 已下载并核验；后续使用者仍需自行申请官方 Hugging Face 访问权限。 |
| RetiZero | retizero-default | CFP;text | [论文](https://www.nature.com/articles/s41467-025-60577-9) · Nature Communications | [18.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics) | RetiZero.pth | 1.65 GB | [官方权重](https://drive.google.com/file/d/14bMmnefO73_NL1Xc4x0A5qFNbuI7GqKM/view) | [官方代码](https://github.com/LooKing9218/RetiZero) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| UrFound | urfound-default | CFP;OCT;text | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70) · MICCAI | 不适用 | urfound_mm.pth | 1.82 GB | [官方权重](https://huggingface.co/yyyyk/UrFound) | [官方代码](https://github.com/yukkai/UrFound) | 从官方 huggingface 页面下载 | 代码采用 MIT，但权重许可范围尚未明确。 | 已下载并核验 |
| ViLReF | vilref-default | CFP;text | [论文](https://arxiv.org/abs/2408.10894) · arXiv | 不适用 | ViLReF_ViT.pt | 753.19 MB | [官方权重](https://drive.google.com/file/d/13YY2Qto4Xzx-gcOJB1kLdp1pqfjZEnxA/view) | [官方代码](https://github.com/T6Yang/ViLReF) | 从官方 google_drive 页面下载 | 官方入口未明确声明权重许可证；限内部研究使用并需自行复核。 | 已下载并核验 |
| VisionFM | visionfm-external-eye | external_eye | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_External_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/16zGHTD4ZcGAYW382kKHBw3TU6D1OtvTD/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-ffa | FFA | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_FFA_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/128izBUNV00Ojb9w9Dq3GhBvhWqzU-mla/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-fundus | CFP | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_Fundus_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/13uWm0a02dCWyARUcrCdHZIcEgRfBmVA4/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-mri | MRI | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_MRI_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/1fcfylnOWhfnZHBAKT9pQPufyS5ZYCXu0/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-oct | OCT | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_OCT_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/1o6E-ine2QLx2pxap-c77u-SU0FjxwypA/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-slit-lamp | slit_lamp | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_SiltLamp_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/1pemWDkGoZYlqLQ6ooFINktyk8xnv9wY_/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-ubm | UBM | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_UBM_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/1q2fVOgFBnWNu1BsXaza1A-OIcCiifNUQ/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionFM | visionfm-ultrasound | ultrasound | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221) · NEJM AI | 尚未核验 | VFM_UltraSound_weights.pth | 1.51 GB | [官方权重](https://drive.google.com/file/d/1IlD0snowxdEVvxmiIBZGR0D9uOcrCT2D/view) | [官方代码](https://github.com/ABILab-CUHK/VisionFM) | 项目已有资产，本轮不重复下载 | 仅限研究、教育和非商业用途。 | 项目初代模型，保留模型信息，但不作为新的外部权重重复下载。 |
| VisionUnite | visionunite-default | CFP;OCT;FFA;MRI;CT;PET;X_ray;text | [论文](https://ieeexplore.ieee.org/document/11124413) · TPAMI | [20.4（2025）](https://innovate.ieee.org/ieee-journals-continue-to-excel-in-citation-rankings/) | checkpoint-VisionUniteV1.pth | 19.19 GB | [官方权重](https://drive.google.com/file/d/1kbdpPklCdDxEgxcpsp4OgGjxvxKh5jpV/view) | [官方代码](https://github.com/HUANGLIZI/VisionUnite) | 从官方 google_drive 页面下载 | 仅限学术研究，不允许商业使用或二次开发。 | 已下载并核验 |

## DERETFound

- 模型简介：眼科视觉基础模型；核心架构为 ViT-L/16 MAE编码器 + ViT-S解码器。
- 输入模态：CFP。
- 发表论文：[论文页面](https://www.nature.com/articles/s41551-025-01365-0)。
- 发表期刊/平台：Nature Biomedical Engineering。
- 影响因子：[26.3（2025）](https://www.nature.com/natbiomedeng/journal-impact)。
- 官方代码：[代码仓库](https://github.com/Jonlysun/DERETFound)。
- 官方权重页面：[deretfound-pretraining](https://zenodo.org/records/13340936/files/PreTraining.zip)；[deretfound-sd-retina](https://zenodo.org/records/13340936/files/sd-retina-model.zip)。
- 已提供 checkpoint：deretfound-pretraining, deretfound-sd-retina。
- 权重文件名：PreTraining.zip, sd-retina-model.zip。
- 文件大小：3.66 GB, 3.19 GB。
- 获取方式：从官方 zenodo 页面下载。
- 是否需要申请：否。
- 当前允许用途：代码仓库存在许可证，但权重是否适用同一许可尚未明确。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/Jonlysun/DERETFound)。
- 官方预处理说明：见 [官方代码](https://github.com/Jonlysun/DERETFound)，不同模型不得默认共用同一预处理。
- 当前状态：deretfound-pretraining：已下载并核验；deretfound-sd-retina：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：deretfound-pretraining = b6b3e92dde5409b18e3dbc6118c6f4d0216545f62cd0a2241f5d20593aafe361；deretfound-sd-retina = df65ab9852adbd06bb223ad09f3df4bec07261c4727ebabc6bb9d7ad09ae89e3。

## EyeCLIP

- 模型简介：视觉-语言眼科基础模型；核心架构为 ViT-Large/16图像编码器 + 文本编码器。
- 输入模态：CFP, OCT, FFA, ICGA, FAF, ultrasound, external_eye, slit_lamp, specular_microscopy, CT, RetCam, text。
- 发表论文：[论文页面](https://www.nature.com/articles/s41746-025-01772-2)。
- 发表期刊/平台：NPJ Digital Medicine。
- 影响因子：[18.0（2025）](https://www.nature.com/npjdigitalmed/journal-impact)。
- 官方代码：[代码仓库](https://github.com/Michi-3000/EyeCLIP)。
- 官方权重页面：[eyeclip-default](https://drive.google.com/file/d/1kWpbDqFCFt4j8RkYqacV4nl-aCKZfqZr/view)。
- 已提供 checkpoint：eyeclip-default。
- 权重文件名：eyeclip.pt。
- 文件大小：2.14 GB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/Michi-3000/EyeCLIP)。
- 官方预处理说明：见 [官方代码](https://github.com/Michi-3000/EyeCLIP)，不同模型不得默认共用同一预处理。
- 当前状态：eyeclip-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：eyeclip-default = dfb6990aa31d55e6eee23f5b79d4b170d86af9d0f533fedaa805f0cdb5d686d4。

## FLAIR

- 模型简介：视觉-语言眼科基础模型；核心架构为 ResNet-50图像编码器 + BioClinicalBERT文本编码器。
- 输入模态：CFP, text。
- 发表论文：[论文页面](https://doi.org/10.1016/j.media.2024.103357)。
- 发表期刊/平台：Medical Image Analysis。
- 影响因子：尚未核验。
- 官方代码：[代码仓库](https://github.com/jusiro/FLAIR)。
- 官方权重页面：[flair-default](https://huggingface.co/jusiro2/FLAIR)。
- 已提供 checkpoint：flair-default。
- 权重文件名：model.safetensors。
- 文件大小：533.32 MB。
- 获取方式：从官方 huggingface 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方声明代码与权重采用 Apache-2.0；使用前仍应保留许可与来源说明。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/jusiro/FLAIR)。
- 官方预处理说明：见 [官方代码](https://github.com/jusiro/FLAIR)，不同模型不得默认共用同一预处理。
- 当前状态：flair-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：flair-default = 050334cd934fa3126435c202c41f493ca222fc3fe3ea9c50cf21f67c792a1440。

## FMUE

- 模型简介：眼科视觉基础模型；核心架构为 RETFound ViT-Large/16编码器 + LoRA + 基于证据学习的Dirichlet不确定性分类器。
- 输入模态：OCT。
- 发表论文：[论文页面](https://doi.org/10.1016/j.xcrm.2024.101876)。
- 发表期刊/平台：Cell Reports Medicine。
- 影响因子：尚未核验。
- 官方代码：[代码仓库](https://github.com/yuanyuanpeng0129/FMUE)。
- 官方权重页面：[fmue-default](https://drive.google.com/file/d/1-rdx6VPJNWVwkjamkplEoyUOHNGweUho/view)。
- 已提供 checkpoint：fmue-default。
- 权重文件名：FMUE.pth。
- 文件大小：1.22 GB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/yuanyuanpeng0129/FMUE)。
- 官方预处理说明：见 [官方代码](https://github.com/yuanyuanpeng0129/FMUE)，不同模型不得默认共用同一预处理。
- 当前状态：fmue-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：fmue-default = ece65c8da05bf89c0666c00e01ee4073ec65c90c47802dcfce5d0fba97152477。

## KeepFIT

- 模型简介：视觉-语言眼科基础模型；核心架构为 ResNet-50图像编码器 + BioClinicalBERT文本编码器 + 视觉文本投影头 + 多头交叉注意力知识修订模块。
- 输入模态：CFP, OCT, text。
- 发表论文：[论文页面](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67)。
- 发表期刊/平台：MICCAI。
- 影响因子：不适用。
- 官方代码：[代码仓库](https://github.com/lxirich/MM-Retinal)。
- 官方权重页面：[keepfit-ffa-ir-mmretinal-ffa](https://drive.google.com/file/d/1fdCRDbKJKZcqBlmdEdETygZ8EsBu5QlV/view)；[keepfit-flair-mmretinal-cfp](https://drive.google.com/file/d/1w6poCkZeqSTHsLYz1R9-z5Ttc0Vw0qSw/view)；[keepfit-half-flair-mmretinal-cfp](https://drive.google.com/file/d/1o4EDSifmcN7cKDP5w5qvS_wWiyfEZ6UN/view)。
- 已提供 checkpoint：keepfit-ffa-ir-mmretinal-ffa, keepfit-flair-mmretinal-cfp, keepfit-half-flair-mmretinal-cfp。
- 权重文件名：KeepFIT (FFA-IR+MM).pth, KeepFIT (flair+MM).pth, KeepFIT (50%flair+MM).pth。
- 文件大小：537.66 MB, 537.66 MB, 537.66 MB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/lxirich/MM-Retinal)。
- 官方预处理说明：见 [官方代码](https://github.com/lxirich/MM-Retinal)，不同模型不得默认共用同一预处理。
- 当前状态：keepfit-ffa-ir-mmretinal-ffa：已下载并核验；keepfit-flair-mmretinal-cfp：已下载并核验；keepfit-half-flair-mmretinal-cfp：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：keepfit-ffa-ir-mmretinal-ffa = ca6610998a1625a96fed21bfb453a58b41f4cc42d2e23116d60b166211f2ecfd；keepfit-flair-mmretinal-cfp = 500904a3cae65f813c74ad9b87c2305c7b375c899fd064fc548c6b1f0e7104c9；keepfit-half-flair-mmretinal-cfp = 12e7fd11f9572f63332c8a3c6e00786d670df02258ee9d5c50a8a311bb70345c。

## MIRAGE

- 模型简介：多模态眼科视觉基础模型；核心架构为 MultiMAE式多模态掩码自编码器：共享ViT编码器 + 模态特异性线性投影层 + 模态特异性Transformer解码器。
- 输入模态：OCT, SLO, retinal_layer_pseudolabels。
- 发表论文：[论文页面](https://www.nature.com/articles/s41746-025-01852-3)。
- 发表期刊/平台：npj Digital Medicine。
- 影响因子：[18.0（2025）](https://www.nature.com/npjdigitalmed/journal-impact)。
- 官方代码：[代码仓库](https://github.com/j-morano/MIRAGE)。
- 官方权重页面：[mirage-base](https://huggingface.co/j-morano/MIRAGE-Base)；[mirage-large](https://huggingface.co/j-morano/MIRAGE-Large)。
- 已提供 checkpoint：mirage-base, mirage-large。
- 权重文件名：model.safetensors, model.safetensors。
- 文件大小：348.11 MB, 1.22 GB。
- 获取方式：从官方 huggingface 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方声明模型与代码采用 CC BY 4.0，使用时需署名。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/j-morano/MIRAGE)。
- 官方预处理说明：见 [官方代码](https://github.com/j-morano/MIRAGE)，不同模型不得默认共用同一预处理。
- 当前状态：mirage-base：已下载并核验；mirage-large：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：mirage-base = bdb3ad174fd8106f32e692446479966ebf095fa8f9a523f9b29185ed0136c339；mirage-large = 22c7da599f82a8d6a252c9df61e43dff22af06a9196a56879a0080cec9f5894c。

## PRETI

- 模型简介：眼科视觉基础模型；核心架构为 ViT-S或ViT-B编码器 + ViT-S解码器 + Learnable Metadata Embedding（LME）+ Retina-Aware Adaptive Masking。
- 输入模态：CFP。
- 发表论文：[论文页面](https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50)。
- 发表期刊/平台：MICCAI。
- 影响因子：不适用。
- 官方代码：[代码仓库](https://github.com/MICV-yonsei/PRETI)。
- 官方权重页面：[preti-default](https://drive.google.com/file/d/1mEFm3bxSPPOm4bLPC9Ey64oeq-6F0S0G/view)。
- 已提供 checkpoint：preti-default。
- 权重文件名：checkpoint-119.pth。
- 文件大小：1.12 GB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/MICV-yonsei/PRETI)。
- 官方预处理说明：见 [官方代码](https://github.com/MICV-yonsei/PRETI)，不同模型不得默认共用同一预处理。
- 当前状态：preti-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：preti-default = c6f7ca533c6d609a691a7f0ac3234bee78fe1116da714d9929308eaeaf409395。

## RET-CLIP

- 模型简介：视觉-语言眼科基础模型；核心架构为 ViT-B/16视觉编码器 + RoBERTa-Base中文文本编码器 + MLP。
- 输入模态：CFP, text。
- 发表论文：[论文页面](https://doi.org/10.1007/978-3-031-72390-2_66)。
- 发表期刊/平台：MICCAI。
- 影响因子：不适用。
- 官方代码：[代码仓库](https://github.com/sStonemason/RET-CLIP)。
- 官方权重页面：[ret-clip-default](https://drive.google.com/file/d/1lYrAg5qzFbNghEW-3UB36v9WL-mo5eN9/view)。
- 已提供 checkpoint：ret-clip-default。
- 权重文件名：ret-clip.pt。
- 文件大小：767.61 MB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/sStonemason/RET-CLIP)。
- 官方预处理说明：见 [官方代码](https://github.com/sStonemason/RET-CLIP)，不同模型不得默认共用同一预处理。
- 当前状态：ret-clip-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：ret-clip-default = 539819ae5ce4c13ea05aa00c5f270eb8432bf02d9ea7f695a9168b97540d1850。

## RETFound

- 模型简介：眼科视觉基础模型；核心架构为 MAE 自监督框架：ViT-Large/16 编码器 + ViT-Small 解码器；下游任务使用 ViT-Large 编码器 + MLP 分类头。
- 输入模态：CFP, OCT。
- 发表论文：[论文页面](https://www.nature.com/articles/s41586-023-06555-x)。
- 发表期刊/平台：Nature。
- 影响因子：[56.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics)。
- 官方代码：[代码仓库](https://github.com/rmaphoh/RETFound)。
- 官方权重页面：[retfound-cfp](https://huggingface.co/YukunZhou/RETFound_mae_natureCFP)；[retfound-oct](https://huggingface.co/YukunZhou/RETFound_mae_natureOCT)。
- 已提供 checkpoint：retfound-cfp, retfound-oct。
- 权重文件名：RETFound_mae_natureCFP.pth, RETFound_mae_natureOCT.pth。
- 文件大小：3.95 GB, 3.95 GB。
- 获取方式：在官方 Hugging Face 页面申请权限并使用本人账号下载。
- 是否需要申请：是。
- 当前允许用途：需接受官方权重访问条款；不得推断允许再分发。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/rmaphoh/RETFound)。
- 官方预处理说明：见 [官方代码](https://github.com/rmaphoh/RETFound)，不同模型不得默认共用同一预处理。
- 当前状态：retfound-cfp：已下载并核验；retfound-oct：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：retfound-cfp = e1e4f66a1b792eeb6e2efaf158f33be35c8255f36b3d17ed67cd5129da246485；retfound-oct = e9ff7864f40334885062953cb3894739d9fff52aaeb22c8b4f47d92270068d18。

## RETFound-Green

- 模型简介：眼科视觉基础模型；核心架构为 ViT-Small + 4个Register Tokens。
- 输入模态：CFP。
- 发表论文：[论文页面](https://www.nature.com/articles/s41467-025-62123-z)。
- 发表期刊/平台：Nature Communications。
- 影响因子：[18.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics)。
- 官方代码：[代码仓库](https://github.com/justinengelmann/RETFound_Green)。
- 官方权重页面：[retfound-green-v0.1](https://github.com/justinengelmann/RETFound_Green/releases/tag/v0.1)。
- 已提供 checkpoint：retfound-green-v0.1。
- 权重文件名：retfoundgreen_statedict.pth。
- 文件大小：87.40 MB。
- 获取方式：从官方 github_release 页面下载。
- 是否需要申请：否。
- 当前允许用途：仅限非商业研究用途；不得推断允许再分发。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/justinengelmann/RETFound_Green)。
- 官方预处理说明：见 [官方代码](https://github.com/justinengelmann/RETFound_Green)，不同模型不得默认共用同一预处理。
- 当前状态：retfound-green-v0.1：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：retfound-green-v0.1 = 431de5dbc1bebbb32f60e2c0bcf8daa4f8bcbf06f7cb1e1dc97ec589713942e1。

## RetiZero

- 模型简介：视觉-语言眼科基础模型；核心架构为 冻结的 RETFound 图像编码器ViT-Large/16 ＋ BioClinicalBERT 文本编码器。
- 输入模态：CFP, text。
- 发表论文：[论文页面](https://www.nature.com/articles/s41467-025-60577-9)。
- 发表期刊/平台：Nature Communications。
- 影响因子：[18.1（2025）](https://www.nature.com/nature-portfolio/about-journals/journal-metrics)。
- 官方代码：[代码仓库](https://github.com/LooKing9218/RetiZero)。
- 官方权重页面：[retizero-default](https://drive.google.com/file/d/14bMmnefO73_NL1Xc4x0A5qFNbuI7GqKM/view)。
- 已提供 checkpoint：retizero-default。
- 权重文件名：RetiZero.pth。
- 文件大小：1.65 GB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/LooKing9218/RetiZero)。
- 官方预处理说明：见 [官方代码](https://github.com/LooKing9218/RetiZero)，不同模型不得默认共用同一预处理。
- 当前状态：retizero-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：retizero-default = 7d06d29441c981898bbb56abdaae1eb97e205448f0a9bc2a68e2aa9431601ede。

## UrFound

- 模型简介：视觉-语言眼科基础模型；核心架构为 共享ViT-B编码器 + 8层图像解码器 + 6层条件语言解码器。
- 输入模态：CFP, OCT, text。
- 发表论文：[论文页面](https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70)。
- 发表期刊/平台：MICCAI。
- 影响因子：不适用。
- 官方代码：[代码仓库](https://github.com/yukkai/UrFound)。
- 官方权重页面：[urfound-default](https://huggingface.co/yyyyk/UrFound)。
- 已提供 checkpoint：urfound-default。
- 权重文件名：urfound_mm.pth。
- 文件大小：1.82 GB。
- 获取方式：从官方 huggingface 页面下载。
- 是否需要申请：否。
- 当前允许用途：代码采用 MIT，但权重许可范围尚未明确。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/yukkai/UrFound)。
- 官方预处理说明：见 [官方代码](https://github.com/yukkai/UrFound)，不同模型不得默认共用同一预处理。
- 当前状态：urfound-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：urfound-default = 8a26bf1a64d449d30fe6fc5faabea48431aa6c15a743d324b8e16271109942e3。

## ViLReF

- 模型简介：视觉-语言眼科基础模型；核心架构为 ViT-B/16图像编码器 + RoBERTa-wwm-ext-base-chinese文本编码器 + 非线性投影头。
- 输入模态：CFP, text。
- 发表论文：[论文页面](https://arxiv.org/abs/2408.10894)。
- 发表期刊/平台：arXiv。
- 影响因子：不适用。
- 官方代码：[代码仓库](https://github.com/T6Yang/ViLReF)。
- 官方权重页面：[vilref-default](https://drive.google.com/file/d/13YY2Qto4Xzx-gcOJB1kLdp1pqfjZEnxA/view)。
- 已提供 checkpoint：vilref-default。
- 权重文件名：ViLReF_ViT.pt。
- 文件大小：753.19 MB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：官方入口未明确声明权重许可证；限内部研究使用并需自行复核。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/T6Yang/ViLReF)。
- 官方预处理说明：见 [官方代码](https://github.com/T6Yang/ViLReF)，不同模型不得默认共用同一预处理。
- 当前状态：vilref-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：vilref-default = 7b0c0597532bfa8492c83d63140d70a9358cd27e86966333981aec3967fe6ef9。

## VisionFM

- 模型简介：多模态眼科基础模型；核心架构为 8个独立ViT-B/16编码器，每个模态一个编码器。
- 输入模态：CFP, OCT, FFA, ultrasound, external_eye, slit_lamp, MRI, UBM。
- 发表论文：[论文页面](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221)。
- 发表期刊/平台：NEJM AI。
- 影响因子：尚未核验。
- 官方代码：[代码仓库](https://github.com/ABILab-CUHK/VisionFM)。
- 官方权重页面：[visionfm-external-eye](https://drive.google.com/file/d/16zGHTD4ZcGAYW382kKHBw3TU6D1OtvTD/view)；[visionfm-ffa](https://drive.google.com/file/d/128izBUNV00Ojb9w9Dq3GhBvhWqzU-mla/view)；[visionfm-fundus](https://drive.google.com/file/d/13uWm0a02dCWyARUcrCdHZIcEgRfBmVA4/view)；[visionfm-mri](https://drive.google.com/file/d/1fcfylnOWhfnZHBAKT9pQPufyS5ZYCXu0/view)；[visionfm-oct](https://drive.google.com/file/d/1o6E-ine2QLx2pxap-c77u-SU0FjxwypA/view)；[visionfm-slit-lamp](https://drive.google.com/file/d/1pemWDkGoZYlqLQ6ooFINktyk8xnv9wY_/view)；[visionfm-ubm](https://drive.google.com/file/d/1q2fVOgFBnWNu1BsXaza1A-OIcCiifNUQ/view)；[visionfm-ultrasound](https://drive.google.com/file/d/1IlD0snowxdEVvxmiIBZGR0D9uOcrCT2D/view)。
- 已提供 checkpoint：visionfm-external-eye, visionfm-ffa, visionfm-fundus, visionfm-mri, visionfm-oct, visionfm-slit-lamp, visionfm-ubm, visionfm-ultrasound。
- 权重文件名：VFM_External_weights.pth, VFM_FFA_weights.pth, VFM_Fundus_weights.pth, VFM_MRI_weights.pth, VFM_OCT_weights.pth, VFM_SiltLamp_weights.pth, VFM_UBM_weights.pth, VFM_UltraSound_weights.pth。
- 文件大小：1.51 GB, 1.51 GB, 1.51 GB, 1.51 GB, 1.51 GB, 1.51 GB, 1.51 GB, 1.51 GB。
- 获取方式：项目已有资产，本轮不重复下载。
- 是否需要申请：否。
- 当前允许用途：仅限研究、教育和非商业用途。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/ABILab-CUHK/VisionFM)。
- 官方预处理说明：见 [官方代码](https://github.com/ABILab-CUHK/VisionFM)，不同模型不得默认共用同一预处理。
- 当前状态：项目初代模型，保留模型信息，但不作为新的外部权重重复下载。
- 后续人员下一步：如后续评估确需使用，复用项目既有 VisionFM 资产并核对 checkpoint 版本。

## VisionUnite

- 模型简介：眼科视觉-语言基础模型；核心架构为 EVA-02/CLIP视觉编码器 + 体征分类Vision Adapter + Vision Projector + LLaMA-7B。
- 输入模态：CFP, OCT, FFA, MRI, CT, PET, X_ray, text。
- 发表论文：[论文页面](https://ieeexplore.ieee.org/document/11124413)。
- 发表期刊/平台：TPAMI。
- 影响因子：[20.4（2025）](https://innovate.ieee.org/ieee-journals-continue-to-excel-in-citation-rankings/)。
- 官方代码：[代码仓库](https://github.com/HUANGLIZI/VisionUnite)。
- 官方权重页面：[visionunite-default](https://drive.google.com/file/d/1kbdpPklCdDxEgxcpsp4OgGjxvxKh5jpV/view)。
- 已提供 checkpoint：visionunite-default。
- 权重文件名：checkpoint-VisionUniteV1.pth。
- 文件大小：19.19 GB。
- 获取方式：从官方 google_drive 页面下载。
- 是否需要申请：否。
- 当前允许用途：仅限学术研究，不允许商业使用或二次开发。
- 商业使用限制：不得从未明确的权重许可推断商业使用权；以官方最新条款为准。
- 再分发限制：本仓库不重新分发第三方权重；除非官方条款明确允许，否则不得再分发。
- 官方加载说明：见 [官方代码](https://github.com/HUANGLIZI/VisionUnite)。
- 官方预处理说明：见 [官方代码](https://github.com/HUANGLIZI/VisionUnite)，不同模型不得默认共用同一预处理。
- 当前状态：visionunite-default：已下载并核验
- 后续人员下一步：按官方代码复现 loader 与原生预处理，完成单模型加载测试后再进入评估。
- SHA256：visionunite-default = fe8a90a592a0fc86e64702df6945ddab72d070871e5d3341375c05ddfbfeb91c。
