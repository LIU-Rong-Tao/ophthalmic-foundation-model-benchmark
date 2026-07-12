# 安装与环境

## Python

支持 Python 3.10 和 3.11；不强制只能使用 3.11。建议每个项目使用独立虚拟环境。

## 安装档位

```bash
pip install -e ".[dev]"                       # 注册表、CLI、测试
pip install -e ".[retfound]"                  # RETFound Adapter
pip install -e ".[frozen-transfer]"           # 冻结特征评测
pip install -e ".[retfound,frozen-transfer]"  # 当前完整 pilot
```

权重不会随安装自动下载。RETFound CFP 属于受控访问权重，必须由使用者从官方来源取得并显式传入路径。

## 启动前检查

```bash
ophbench registry validate
ophbench catalog build --check
ophbench doctor --model retfound
```

GPU、CUDA 与 PyTorch 版本应记录在每次运行的 `run_manifest.json` 中。
