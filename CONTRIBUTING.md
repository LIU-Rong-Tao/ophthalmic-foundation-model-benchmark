# 贡献指南

欢迎提交新模型、补充 checkpoint 或更正已有记录。当前贡献重点是可追踪的模型资产信息，不要求同时实现 Adapter。

## 提交内容

- 模型正式名称、论文、官方代码、模态和核心架构；
- 官方 checkpoint、权重入口、访问条件和许可证信息；
- 官方预处理是否有明确说明；
- 论文或官方代码是否报告可输出特征；
- 每项“已核验”结论对应的官方来源链接；
- 可选的 Adapter 与 smoke 结果。

## 规则

1. 使用独立分支和 Pull Request，不直接提交到 `main`。
2. 复制 `templates/model.yaml` 与 `templates/checkpoint.yaml`，ID 使用 kebab-case。
3. 未核验信息保持 `null`、`unknown`、`false` 或对应的待核验状态，不根据常识猜测。
4. 不上传权重、医学数据、访问 token 或私有链接。
5. 不把论文报告结果表述为本项目复现结果。
6. 不手工编辑 `MODEL_ZOO.md` 和 `catalog/`。

## 提交前检查

```bash
ophbench registry validate
ophbench catalog build
ophbench catalog build --check
pytest -q
```

核验口径见 `docs/verification_status.md`。
