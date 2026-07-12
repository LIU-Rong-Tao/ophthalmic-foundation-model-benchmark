# 新增模型

## 最小步骤

1. 复制 `templates/model.yaml`，填写模型级信息。
2. 为每个官方 checkpoint 复制 `templates/checkpoint.yaml`。
3. 在 notes 或 PR 描述中列出核验使用的官方证据。
4. 运行注册表校验和目录生成。

## 必须优先核验

- 论文与官方代码是否对应同一模型；
- 输入模态和 checkpoint 模态；
- 权重链接、是否需要认证/申请及是否允许重新分发；
- 许可证是否明确；
- 官方预处理说明是否存在；
- 是否报告或提供图像特征输出接口。

Adapter 不是收录模型的前置条件。只有进入团队评测计划的模型，才需要继续实现 `load`、`preprocess` 和 `encode_image`。
