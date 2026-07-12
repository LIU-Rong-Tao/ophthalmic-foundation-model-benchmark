# 评测 Track

## Frozen Feature Transfer v0.1

固定流程：模型原生预处理 → 冻结编码器 → train 拟合 Logistic Regression → val 选择 C → test 评测一次。

第一版主指标为 QWK，次要指标包括 Macro-F1、Accuracy、各类别召回率、混淆矩阵和 image-level bootstrap 95% CI。

RETFound + APTOS2019 当前只承担协议 pilot。只有在第二个同模态模型按相同 split、探针和评测规则运行后，才能进入公平模型比较。
