"""Generate, tile, stitch, and verify a tiny GeoTIFF."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.transform import from_origin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_process import stitch_geotiff_tiles, tile_geotiff


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        workdir = Path(temp_dir)
        source = workdir / "source.tif"
        tiles_dir = workdir / "tiles"
        stitched = workdir / "stitched.tif"

        data = np.arange(3 * 24 * 32, dtype=np.uint16).reshape(3, 24, 32)
        transform = from_origin(500000, 4100000, 2, 2)
        profile = {
            "driver": "GTiff",
            "height": data.shape[1],
            "width": data.shape[2],
            "count": data.shape[0],
            "dtype": data.dtype,
            "crs": "EPSG:32633",
            "transform": transform,
            "nodata": 65535,
        }

        with rasterio.open(source, "w", **profile) as dst:
            dst.write(data)

        tile_geotiff(source, tiles_dir, tile_width=8, tile_height=6)
        stitch_geotiff_tiles(tiles_dir, stitched)

        with rasterio.open(source) as original, rasterio.open(stitched) as rebuilt:
            assert np.array_equal(original.read(), rebuilt.read())
            assert original.crs == rebuilt.crs
            assert original.transform == rebuilt.transform
            assert original.res == rebuilt.res
            assert original.nodata == rebuilt.nodata

        print(f"Round trip succeeded: {stitched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
