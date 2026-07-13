# 下载与文件核验

本 GitHub 仓库不包含第三方模型权重。后续负责人应从 [模型权重总目录](MODEL_WEIGHT_CATALOG.md) 中列出的官方页面，在自己的服务器重新下载。

## 基本规则

1. 不从本项目重新分发第三方权重；
2. gated 模型必须由使用者使用本人账号申请官方访问权限；
3. 下载后同时核对 filename、文件大小与 SHA256；
4. SHA256 相同表示文件内容逐字节一致，但不能单独证明下载网页属于官方来源；
5. 官方身份应结合论文、官方代码仓库和官方权重页面核验；
6. 许可证不明确时，不得推断允许商业使用、二次开发或再分发。

## 推荐目录

    model_cache/
      <model_id>/
        <checkpoint_id>/
          <filename>

## Linux 核验

    sha256sum <filename>

同时使用 ls -l <filename> 或 stat <filename> 核对精确文件大小。

## Python 核验

    python -c "
    import hashlib
    from pathlib import Path
    p = Path('<filename>')
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    print(h.hexdigest())
    "

机器可读的期望文件名、精确 size_bytes 和 SHA256 见 [download_manifest.csv](../catalog/download_manifest.csv)。
