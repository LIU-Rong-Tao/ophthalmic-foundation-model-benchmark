# 快速开始

## 1. 检查注册表

```bash
ophbench registry validate
ophbench list-models
ophbench show-model retfound
```

## 2. 准备本地资产

- 从官方来源获取 RETFound CFP checkpoint；
- 准备固定的 APTOS2019 `train/val/test` 图像目录；
- 不要把权重和医学图像提交到仓库。

## 3. 运行 pilot

使用 README 中的 `scripts/run_frozen_feature_transfer.py` 命令。首次运行会执行模型原生预处理和特征提取；当前脚本不应覆盖非空输出目录。

## 4. 核验结果

重点检查：

- `test_used_for_selection=false`；
- split fingerprint 和 checkpoint SHA256；
- `evaluation_role=pilot_protocol_validation`；
- `research_claim_status=not_for_scientific_comparison`；
- 预测概率列与标签空间一致。
