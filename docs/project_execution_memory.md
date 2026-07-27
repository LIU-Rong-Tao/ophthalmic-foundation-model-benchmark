# v0.3 执行记忆

- A6000 使用 `jxin@192.168.100.30`；严禁配置或使用任何代理。执行前清除 `http_proxy`、`https_proxy`、`HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`。
- 既有 v0.2 工作区 `/data3/jxin/projects/ophthalmic-foundation-model-benchmark` 是脏工作区，不得 reset、clean、覆盖或用于 v0.3 验收。
- v0.3 隔离验收副本固定为 `/data3/jxin/projects/ophbench-v03-standalone`；若需同步本地已提交分支，优先从本机生成完整 Git bundle 并经 SSH/SCP 传入 A6000。原仓库是 partial clone，`git worktree add` 会触发直连 GitHub 补对象并可能卡住，不作为默认路径。
- A6000 复用环境固定为 `/data3/jxin/conda-envs/ophbench/bin/python` 与对应 `pip`；不要新建 Conda 环境。命令行工具应使用该环境的 `python -m <tool>`，不要假设 `ruff`、`pytest` 等 console entry 位于 PATH。
- RETFound CFP 本地 checkpoint：`/data3/jxin/New_RETFound/RETFound_mae_natureCFP/RETFound_mae_natureCFP.pth`。仅本地显式加载，不下载权重。
