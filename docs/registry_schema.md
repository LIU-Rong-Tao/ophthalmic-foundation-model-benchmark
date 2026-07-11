# Registry schema

`registry/models/<model_id>.yaml` 与 `registry/checkpoints/<checkpoint_id>.yaml` 是唯一权威数据源。JSON Schema 位于 `registry/schemas/`，由 importer 从 Pydantic 模型生成。每条记录保留 provenance；未知信息使用 `null`、`unknown` 或 `false`，禁止猜测。

模型的 `reported_summary` 和 `reported_tasks_text` 来自 seed 表格，不是本项目实验结果。checkpoint 的 `redistribution_allowed: unknown` 不应解释为允许再分发。
