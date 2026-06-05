"""Backward-compatible wrappers for GeoTIFF tiling and stitching.

The original project exposed ``clip_one_picture`` and ``merge_picture`` from
this script. New code should prefer ``data_process.raster`` or the
``data-process`` command line interface.
"""

from __future__ import annotations

import os
from pathlib import Path

from data_process.raster import stitch_geotiff_tiles, tile_geotiff


def clip_one_picture(path, filename, cols, rows):
    """Split ``path/filename`` into ``crop{cols}_{rows}`` GeoTIFF tiles."""

    input_path = Path(path) / filename
    save_path = Path(path) / f"crop{cols}_{rows}"
    tiles = tile_geotiff(
        input_path,
        save_path,
        cols,
        rows,
        full_tiles_only=True,
        overwrite=True,
        legacy_names=True,
    )
    print(f"Clipped {input_path} into {len(tiles)} tile(s): {save_path}")
    return tiles


def merge_picture(merge_path, num_of_cols=None, num_of_rows=None):
    """Stitch tiles in ``merge_path`` into ``merge.tif``.

    ``num_of_cols`` and ``num_of_rows`` are accepted for compatibility with
    the original script. Tile positions are now read from filenames.
    """

    output_path = Path(merge_path) / "merge.tif"
    result = stitch_geotiff_tiles(merge_path, output_path, overwrite=True)
    print(f"Merged tiles into {result}")
    return result


def file_name(root_path, picturetype):
    """Return files with the requested extension under ``root_path``."""

    filename = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if os.path.splitext(file)[1] == picturetype:
                filename.append(os.path.join(root, file))
    return filename


if __name__ == "__main__":
    print("Use `data-process --help` for the command line interface.")
