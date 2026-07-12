# 核验状态

## 模型信息

- `seed_unverified`：来自 seed，尚未逐项用官方来源核验；
- `partially_verified`：至少部分核心字段已由官方来源或真实运行核验；
- `verified`：规定的核心字段均已核验。

## 权重

- **待核验**：只有登记链接或访问声明；
- **入口已核验**：确认官方权重入口和访问条件；
- **文件已核验**：本地文件与记录的哈希相符。

## Adapter 与特征提取

- `not_started`：未实现；
- `implemented`：已实现统一接口；
- smoke `passed`：真实 checkpoint 已完成加载、预处理和 embedding 输出验证。

“已收录”不能替代上述任何核验状态。
