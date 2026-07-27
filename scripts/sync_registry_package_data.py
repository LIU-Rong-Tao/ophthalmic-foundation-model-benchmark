import runpy
from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    namespace = runpy.run_path(str(root / "build_support.py"))
    namespace["sync_registry_data"](root)
