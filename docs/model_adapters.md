# 模型 Adapter

图像编码 Adapter 必须实现：`check_environment()`、`load()`、`preprocess(image)` 和 `encode_image(tensor)`。

Adapter 负责模型原生预处理与真实 checkpoint 加载，不能用随机权重或占位输出冒充支持。当前只有 `retfound / retfound-cfp` 已验证。

新增 Adapter 前必须核验官方代码、checkpoint 对应版本、访问条件、许可证、输入尺寸、归一化与 embedding 维度。smoke test 只证明加载和编码链路可执行，不等于下游 benchmark 结果。
