import sys

from ophbench.cli import app

if __name__ == "__main__":
    app(["catalog", "build", *sys.argv[1:]])
