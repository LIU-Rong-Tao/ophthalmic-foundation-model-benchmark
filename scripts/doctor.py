import sys

from ophbench.cli import app

if __name__ == "__main__":
    app(["doctor", *sys.argv[1:]])
