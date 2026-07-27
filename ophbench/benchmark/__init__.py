"""脱敏的 benchmark 结果契约、导入和静态页面数据构建。"""

from .builder import build_benchmark
from .importer import import_benchmark_run

__all__ = ["build_benchmark", "import_benchmark_run"]
