from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from data_process import stitch_geotiff_tiles, tile_geotiff


def _write_test_geotiff(path):
    data = np.arange(3 * 24 * 32, dtype=np.uint16).reshape(3, 24, 32)
    profile = {
        "driver": "GTiff",
        "height": data.shape[1],
        "width": data.shape[2],
        "count": data.shape[0],
        "dtype": data.dtype,
        "crs": "EPSG:32633",
        "transform": from_origin(500000, 4100000, 2, 2),
        "nodata": 65535,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data)
    return data, profile


class RasterProcessingTest(unittest.TestCase):
    def test_geotiff_tile_stitch_roundtrip_preserves_data_and_spatial_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source.tif"
            tiles_dir = tmp_path / "tiles"
            stitched = tmp_path / "stitched.tif"
            expected_data, _ = _write_test_geotiff(source)

            tiles = tile_geotiff(source, tiles_dir, tile_width=8, tile_height=6)
            self.assertEqual(len(tiles), 16)

            stitch_geotiff_tiles(tiles_dir, stitched)

            with rasterio.open(source) as original, rasterio.open(stitched) as rebuilt:
                self.assertTrue(np.array_equal(rebuilt.read(), expected_data))
                self.assertTrue(np.array_equal(original.read(), rebuilt.read()))
                self.assertEqual(original.crs, rebuilt.crs)
                self.assertEqual(original.transform, rebuilt.transform)
                self.assertEqual(original.res, rebuilt.res)
                self.assertEqual(original.nodata, rebuilt.nodata)
                self.assertEqual(original.count, rebuilt.count)
                self.assertEqual(original.dtypes, rebuilt.dtypes)
                self.assertEqual(original.width, rebuilt.width)
                self.assertEqual(original.height, rebuilt.height)

    def test_partial_edges_are_skipped_by_default_and_supported_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source.tif"
            tiles_dir = tmp_path / "tiles"
            partial_tiles_dir = tmp_path / "partial_tiles"
            data = np.arange(1 * 10 * 10, dtype=np.uint16).reshape(1, 10, 10)
            profile = {
                "driver": "GTiff",
                "height": 10,
                "width": 10,
                "count": 1,
                "dtype": data.dtype,
                "crs": "EPSG:4326",
                "transform": from_origin(0, 10, 1, 1),
                "nodata": 65535,
            }
            with rasterio.open(source, "w", **profile) as dst:
                dst.write(data)

            full_only = tile_geotiff(source, tiles_dir, tile_width=6, tile_height=6)
            self.assertEqual(
                [(tile.row, tile.col, tile.width, tile.height) for tile in full_only],
                [(0, 0, 6, 6)],
            )

            with_partials = tile_geotiff(
                source,
                partial_tiles_dir,
                tile_width=6,
                tile_height=6,
                full_tiles_only=False,
            )
            self.assertEqual(
                sorted((tile.row, tile.col, tile.width, tile.height) for tile in with_partials),
                [(0, 0, 6, 6), (0, 1, 4, 6), (1, 0, 6, 4), (1, 1, 4, 4)],
            )

    def test_stitch_rejects_incomplete_tile_grid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source.tif"
            tiles_dir = tmp_path / "tiles"
            stitched = tmp_path / "stitched.tif"
            _write_test_geotiff(source)

            tile_geotiff(source, tiles_dir, tile_width=8, tile_height=6)
            (tiles_dir / "source_r0001_c0001.tif").unlink()

            with self.assertRaisesRegex(ValueError, "incomplete"):
                stitch_geotiff_tiles(tiles_dir, stitched)


if __name__ == "__main__":
    unittest.main()
