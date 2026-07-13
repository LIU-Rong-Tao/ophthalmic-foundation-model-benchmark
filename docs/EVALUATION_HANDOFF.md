# 下一阶段评估交接

本文件只说明第二板块负责人接手后的工作边界，不设计具体评测指标，也不实现特征提取代码。

## 交接入口

- 模型清单：[MODEL_WEIGHT_CATALOG.md](MODEL_WEIGHT_CATALOG.md)
- 机器下载清单：[download_manifest.csv](../catalog/download_manifest.csv)
- 下载与核验说明：[DOWNLOAD_AND_VERIFY.md](DOWNLOAD_AND_VERIFY.md)

权重不包含在 GitHub 仓库中。下一阶段负责人需要在自己的服务器从官方页面重新下载，并按 checkpoint_id、filename、size_bytes 和 SHA256 核验。

## 下一阶段工作

1. 按 CFP、OCT 和多模态模型分组；
2. 逐个复现模型官方预处理，不默认让不同模型共用同一预处理；
3. 完成单模型加载测试；
4. 在加载与预处理确认后批量提取特征；
5. 在 UKB 和外部队列上完成后续评估。

## 特殊状态

- VisionFM 是本项目初代模型，保留模型信息，但不作为新的外部模型重复下载；后续如需比较，应复用并核对项目已有资产。
- RETFound CFP/OCT 当前服务器资产已完成官方文件核验；新负责人仍须使用本人 Hugging Face 账号申请官方 gated access 后重新下载。

每次实验必须记录 model_id、checkpoint_id、SHA256、官方预处理版本和数据划分，避免同名模型或不同权重版本混淆。
