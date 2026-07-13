# 眼科基础模型权重总目录

OphBench 第一版收录 **15 个模型、27 个 checkpoint**。主表按模型合并展示，便于在 GitHub 页面直接阅读；逐 checkpoint 的精确文件名、bytes、SHA256 和许可证字段保留在 [机器清单](../catalog/download_manifest.csv) 中。

> 影响因子只反映论文发表平台，不代表模型性能或与具体任务的适配程度。

## 模型总览

| 模型 | 输入模态 | 论文与代码 | Checkpoint、区别与文件 | 当前状态 |
|---|---|---|---|---|
| **DERETFound** | CFP | [论文](https://www.nature.com/articles/s41551-025-01365-0)<br>Nature Biomedical Engineering<br>IF 26.3（2025）<br>[代码](https://github.com/Jonlysun/DERETFound) | [`deretfound-pretraining`](https://zenodo.org/records/13340936/files/PreTraining.zip) · MAE 基础预训练权重，用于下游微调和特征迁移<br><sub>PreTraining.zip · 3.66 GB</sub><br><br>[`deretfound-sd-retina`](https://zenodo.org/records/13340936/files/sd-retina-model.zip) · 视网膜 Stable Diffusion 生成模型，不是分类/特征编码权重<br><sub>sd-retina-model.zip · 3.19 GB</sub> | ✅ 2/2 已下载核验 |
| **EyeCLIP** | **12 种**<br><sub>CFP、OCT、FFA、ICGA、FAF、B超、外眼、裂隙灯、角膜内皮显微镜、CT、RetCam、文本</sub> | [论文](https://www.nature.com/articles/s41746-025-01772-2)<br>NPJ Digital Medicine<br>IF 18.0（2025）<br>[代码](https://github.com/Michi-3000/EyeCLIP) | [`eyeclip-default`](https://drive.google.com/file/d/1kWpbDqFCFt4j8RkYqacV4nl-aCKZfqZr/view) · 官方默认预训练权重<br><sub>eyeclip.pt · 2.14 GB</sub> | ✅ 1/1 已下载核验 |
| **FLAIR** | CFP、文本 | [论文](https://doi.org/10.1016/j.media.2024.103357)<br>Medical Image Analysis<br>IF 待核验<br>[代码](https://github.com/jusiro/FLAIR) | [`flair-default`](https://huggingface.co/jusiro2/FLAIR) · 官方默认预训练权重<br><sub>model.safetensors · 533.32 MB</sub> | ✅ 1/1 已下载核验 |
| **FMUE** | OCT | [论文](https://doi.org/10.1016/j.xcrm.2024.101876)<br>Cell Reports Medicine<br>IF 待核验<br>[代码](https://github.com/yuanyuanpeng0129/FMUE) | [`fmue-default`](https://drive.google.com/file/d/1-rdx6VPJNWVwkjamkplEoyUOHNGweUho/view) · 官方默认预训练权重<br><sub>FMUE.pth · 1.22 GB</sub> | ✅ 1/1 已下载核验 |
| **KeepFIT** | CFP、FFA | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72378-0_67)<br>MICCAI<br>[代码](https://github.com/lxirich/MM-Retinal) | [`keepfit-ffa-ir-mmretinal-ffa`](https://drive.google.com/file/d/1fdCRDbKJKZcqBlmdEdETygZ8EsBu5QlV/view) · FFA；使用 FFA-IR + MM-Retinal 训练<br><sub>KeepFIT (FFA-IR+MM).pth · 537.66 MB</sub><br><br>[`keepfit-flair-mmretinal-cfp`](https://drive.google.com/file/d/1w6poCkZeqSTHsLYz1R9-z5Ttc0Vw0qSw/view) · CFP；使用完整 FLAIR + MM-Retinal 训练<br><sub>KeepFIT (flair+MM).pth · 537.66 MB</sub><br><br>[`keepfit-half-flair-mmretinal-cfp`](https://drive.google.com/file/d/1o4EDSifmcN7cKDP5w5qvS_wWiyfEZ6UN/view) · CFP；只使用 50% FLAIR + MM-Retinal<br><sub>KeepFIT (50%flair+MM).pth · 537.66 MB</sub> | ✅ 3/3 已下载核验 |
| **MIRAGE** | OCT、SLO | [论文](https://www.nature.com/articles/s41746-025-01852-3)<br>npj Digital Medicine<br>IF 18.0（2025）<br>[代码](https://github.com/j-morano/MIRAGE) | [`mirage-base`](https://huggingface.co/j-morano/MIRAGE-Base) · ViT-Base 版本，文件更小<br><sub>model.safetensors · 348.11 MB</sub><br><br>[`mirage-large`](https://huggingface.co/j-morano/MIRAGE-Large) · ViT-Large 版本，容量更大<br><sub>model.safetensors · 1.22 GB</sub> | ✅ 2/2 已下载核验 |
| **PRETI** | CFP | [论文](https://link.springer.com/chapter/10.1007/978-3-032-04927-8_50)<br>MICCAI<br>[代码](https://github.com/MICV-yonsei/PRETI) | [`preti-default`](https://drive.google.com/file/d/1mEFm3bxSPPOm4bLPC9Ey64oeq-6F0S0G/view) · 官方默认预训练权重<br><sub>checkpoint-119.pth · 1.12 GB</sub> | ✅ 1/1 已下载核验 |
| **RET-CLIP** | CFP、文本 | [论文](https://doi.org/10.1007/978-3-031-72390-2_66)<br>MICCAI<br>[代码](https://github.com/sStonemason/RET-CLIP) | [`ret-clip-default`](https://drive.google.com/file/d/1lYrAg5qzFbNghEW-3UB36v9WL-mo5eN9/view) · 官方默认预训练权重<br><sub>ret-clip.pt · 767.61 MB</sub> | ✅ 1/1 已下载核验 |
| **RETFound** | CFP、OCT | [论文](https://www.nature.com/articles/s41586-023-06555-x)<br>Nature<br>IF 56.1（2025）<br>[代码](https://github.com/rmaphoh/RETFound) | [`retfound-cfp`](https://huggingface.co/YukunZhou/RETFound_mae_natureCFP) · CFP 专用预训练编码器<br><sub>RETFound_mae_natureCFP.pth · 3.95 GB</sub><br><br>[`retfound-oct`](https://huggingface.co/YukunZhou/RETFound_mae_natureOCT) · OCT 专用预训练编码器<br><sub>RETFound_mae_natureOCT.pth · 3.95 GB</sub> | ✅ 2/2 已下载核验<br>🔐 新服务器需申请 HF 权限 |
| **RETFound-Green** | CFP | [论文](https://www.nature.com/articles/s41467-025-62123-z)<br>Nature Communications<br>IF 18.1（2025）<br>[代码](https://github.com/justinengelmann/RETFound_Green) | [`retfound-green-v0.1`](https://github.com/justinengelmann/RETFound_Green/releases/tag/v0.1) · 官方默认预训练权重<br><sub>retfoundgreen_statedict.pth · 87.40 MB</sub> | ✅ 1/1 已下载核验 |
| **RetiZero** | CFP、文本 | [论文](https://www.nature.com/articles/s41467-025-60577-9)<br>Nature Communications<br>IF 18.1（2025）<br>[代码](https://github.com/LooKing9218/RetiZero) | [`retizero-default`](https://drive.google.com/file/d/14bMmnefO73_NL1Xc4x0A5qFNbuI7GqKM/view) · 官方默认预训练权重<br><sub>RetiZero.pth · 1.65 GB</sub> | ✅ 1/1 已下载核验 |
| **UrFound** | CFP、OCT、文本 | [论文](https://link.springer.com/chapter/10.1007/978-3-031-72390-2_70)<br>MICCAI<br>[代码](https://github.com/yukkai/UrFound) | [`urfound-default`](https://huggingface.co/yyyyk/UrFound) · 官方默认预训练权重<br><sub>urfound_mm.pth · 1.82 GB</sub> | ✅ 1/1 已下载核验 |
| **ViLReF** | CFP、文本 | [论文](https://arxiv.org/abs/2408.10894)<br>arXiv<br>[代码](https://github.com/T6Yang/ViLReF) | [`vilref-default`](https://drive.google.com/file/d/13YY2Qto4Xzx-gcOJB1kLdp1pqfjZEnxA/view) · 官方默认预训练权重<br><sub>ViLReF_ViT.pt · 753.19 MB</sub> | ✅ 1/1 已下载核验 |
| **VisionFM** | **8 种**<br><sub>CFP、OCT、FFA、B超、外眼、裂隙灯、MRI、UBM</sub> | [论文](https://ai.nejm.org/doi/abs/10.1056/AIoa2300221)<br>NEJM AI<br>IF 待核验<br>[代码](https://github.com/ABILab-CUHK/VisionFM) | 8 个模态专用编码器<br><sub>逐项权重文件与下载入口见机器清单</sub> | 项目初代模型<br>保留 8 种模态信息<br>不重复下载 |
| **VisionUnite** | **8 种**<br><sub>CFP、OCT、FFA、MRI、CT、PET、X-ray、文本</sub> | [论文](https://ieeexplore.ieee.org/document/11124413)<br>TPAMI<br>IF 20.4（2025）<br>[代码](https://github.com/HUANGLIZI/VisionUnite) | [`visionunite-default`](https://drive.google.com/file/d/1kbdpPklCdDxEgxcpsp4OgGjxvxKh5jpV/view) · 官方默认预训练权重<br><sub>checkpoint-VisionUniteV1.pth · 19.19 GB</sub> | ✅ 1/1 已下载核验 |

## 同一模型的多个 checkpoint 怎么选

### DERETFound

- **`deretfound-pretraining`**：RETFound-DE 的 MAE 基础预训练模型，用于下游分类微调或冻结特征迁移。
- **`deretfound-sd-retina`**：配套的视网膜 Stable Diffusion 生成模型，用于生成合成视网膜图像。它不是分类编码器，加载方法和用途都与预训练权重不同。

### KeepFIT

- **`keepfit-flair-mmretinal-cfp`**：CFP 模型，使用完整 FLAIR 数据与 MM-Retinal。
- **`keepfit-half-flair-mmretinal-cfp`**：CFP 消融版本，只使用 50% FLAIR 数据与 MM-Retinal。
- **`keepfit-ffa-ir-mmretinal-ffa`**：FFA 模型，训练来源改为 FFA-IR 与 MM-Retinal；不能当作 CFP 权重使用。

### MIRAGE

- **`mirage-base`**：ViT-Base 版本，348.11 MB，适合先验证加载流程。
- **`mirage-large`**：ViT-Large 版本，1.22 GB，模型容量和资源需求更高。
- 两者都处理 OCT/SLO，主要区别是骨干规模，不是输入模态。

### RETFound

- **`retfound-cfp`**：CFP 预训练编码器，只用于彩色眼底照片。
- **`retfound-oct`**：OCT 预训练编码器，只用于 OCT 图像。
- 两者架构相近，但训练模态和权重不同，不能直接互换。新服务器下载时均需使用者自行申请 Hugging Face 权限。

### VisionFM

VisionFM 官方为 8 种模态分别提供独立编码器：**CFP、OCT、FFA、B超、外眼、裂隙灯、MRI、UBM**。本项目已经有 VisionFM 初代资产，因此这里保留全部模型和权重入口信息，但不把它们作为新外部模型重复下载。后续使用时应按输入模态选择对应权重。

## 下载与完整性核验

- 已下载并核验：19 个 checkpoint；
- 项目范围排除重复下载：8 个 VisionFM checkpoint；
- 新负责人应从官方页面重新获取权重，操作方法见 [下载与文件核验](DOWNLOAD_AND_VERIFY.md)；
- 精确 size_bytes、SHA256、访问方式和许可证原始状态见 [download_manifest.csv](../catalog/download_manifest.csv)。
