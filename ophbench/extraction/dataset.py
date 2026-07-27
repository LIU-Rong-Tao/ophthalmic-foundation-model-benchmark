from __future__ import annotations

from pathlib import Path


def open_rgb_image(source_path: str):
    from PIL import Image

    path = Path(source_path)
    with Image.open(path) as image:
        image.load()
        return image.convert("RGB")
