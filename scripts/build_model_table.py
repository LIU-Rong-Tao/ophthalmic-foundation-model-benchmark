from pathlib import Path

from ophbench.registry.builder import build_catalog

if __name__ == "__main__":
    print(build_catalog(Path("registry"), Path("catalog"), model_zoo_path=Path("MODEL_ZOO.md")))
