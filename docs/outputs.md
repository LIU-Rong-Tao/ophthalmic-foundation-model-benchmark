# 输出与复现

`run_manifest.json` 是运行追踪入口，应记录源码 commit、OphBench/Adapter 版本、checkpoint SHA256、split fingerprint、随机种子、选定超参数和 Python/PyTorch/CUDA 环境。

`artifact_manifest.json` 记录产物哈希；`test_predictions.csv` 与 `metrics.json` 可由下游系统只读消费。报告文案或 manifest 字段变化不应触发重新提取特征；完整 feature cache/resume engine 是 v0.2 后续工程项，当前不得宣称已经完成。
