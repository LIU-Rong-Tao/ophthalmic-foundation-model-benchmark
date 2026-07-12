#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ophbench.evaluation import run_frozen_feature_transfer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--checkpoint-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    run_frozen_feature_transfer(
        args.protocol,
        data_root=args.data_root,
        checkpoint_path=args.checkpoint_path,
        output_dir=args.output_dir,
        device=args.device,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
