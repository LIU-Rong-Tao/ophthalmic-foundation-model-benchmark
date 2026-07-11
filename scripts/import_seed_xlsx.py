import sys

from ophbench.cli import app

if __name__ == "__main__":
    app(["registry", "import-seed", *sys.argv[1:]])
