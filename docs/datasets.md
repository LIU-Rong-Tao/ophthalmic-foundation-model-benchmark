# 数据集约定

当前 APTOS2019 pilot 使用冻结的 image-level `train/val/test` 划分。由于没有可靠患者 ID，不得描述为 patient-level split。

split manifest 至少记录相对路径、标签、split、类别分布、重复路径检查和 SHA256 fingerprint。后续数据集接入应提供稳定 `sample_id`、可选 `patient_id`、模态、标签空间与数据集 fingerprint。
