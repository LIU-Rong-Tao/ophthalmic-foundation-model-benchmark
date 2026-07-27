"""可恢复的、与数据集无关的冻结图像特征提取接口。"""

from .runner import ExtractionError, run_extraction
from .schemas import ExtractionConfig, ExtractionResult

__all__ = ["ExtractionConfig", "ExtractionError", "ExtractionResult", "run_extraction"]
