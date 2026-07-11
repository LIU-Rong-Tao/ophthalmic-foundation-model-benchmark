# Contributing

- 不直接向 `main` 提交；每个模型或修改使用独立分支并通过 Pull Request 合入。
- 修改 YAML 后运行 `ophbench registry validate` 与 `ophbench catalog build`。
- 不手工编辑 `MODEL_ZOO.md` 或 `catalog/` 下的生成文件。
- 不上传模型权重、医院/UKB 等医学数据、访问 token 或私有链接。
- 新增或更正官方信息时提供来源 URL，并保持未核验字段为 `null`、`unknown` 或 `false`。
- 不把论文或 seed 表格宣称的结果表述成本项目复现结果。
