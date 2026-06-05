"""Simple image augmentation helpers kept for compatibility."""

from __future__ import annotations

import os
from pathlib import Path

import cv2


def file_name(root_path: str | Path, picturetype: str) -> list[str]:
    """Return files with the requested extension under ``root_path``."""

    root_path = str(root_path)
    filenames: list[str] = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if Path(file).suffix == picturetype:
                filenames.append(os.path.join(root, file))
    return filenames


def rotate(root_path: str | Path, rotation: int, picturetype: str) -> list[Path]:
    """Rotate every matching image by multiples of ``rotation`` up to 360 degrees."""

    if rotation <= 0 or 360 % rotation != 0:
        raise ValueError("rotation must be a positive divisor of 360")

    written: list[Path] = []
    for image_path in file_name(root_path, picturetype):
        img = cv2.imread(image_path, 1)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        rows, cols = img.shape[:2]
        base = Path(image_path)
        for index in range(int(360 / rotation)):
            matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), rotation * index, 1)
            rotated = cv2.warpAffine(img, matrix, (cols, rows))
            output_path = base.with_name(f"{base.stem}_{index}{base.suffix}")
            cv2.imwrite(str(output_path), rotated)
            written.append(output_path)

    return written
