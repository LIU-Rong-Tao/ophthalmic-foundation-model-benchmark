import sys

from ophbench.cli import app

if __name__ == "__main__":
    app(["registry", "validate", *sys.argv[1:]])
