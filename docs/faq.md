# 常见问题

## 15 个模型是否都能运行？

不能。当前只有 RETFound CFP Adapter 已验证，其余主要是待核验元数据。

## 为什么不自动下载权重？

部分权重需要认证、申请或接受单独许可证；OphBench 不绕过这些访问条件。

## smoke test 是 benchmark 吗？

不是。smoke 只验证加载、预处理和 embedding 输出链路。

## 为什么 APTOS pilot 不能声称患者级泛化？

当前划分没有可靠患者 ID，只能声明 image-level split。

## 为什么暂时不接入第二个模型？

必须先审核权重、许可证、预处理与代码版本，避免登记信息被误当成可运行资产。
