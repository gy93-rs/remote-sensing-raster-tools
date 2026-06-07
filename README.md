# remote-sensing-raster-tools

`remote-sensing-raster-tools` is a small Python toolkit for processing large remote sensing images, satellite imagery, and aerial imagery. It focuses on two practical GeoTIFF workflows:

- splitting a large GeoTIFF into fixed-size raster tiles;
- stitching those tiles back into a GeoTIFF mosaic.

The installable Python package remains `data_process` for compatibility with the original repository. The project also keeps a simple image rotation helper from the original scripts.

## Why This Project Matters

Large remote sensing rasters are often too large for direct model training, manual inspection, lightweight data review, or simple processing pipelines. This project provides a focused, testable foundation for splitting and rebuilding GeoTIFF imagery while preserving geospatial metadata.

## Current Capabilities

### GeoTIFF Tiling

The tiling code reads an input GeoTIFF and writes non-overlapping `.tif` tiles. Each output tile preserves:

- coordinate reference system (CRS);
- affine transform for the tile window;
- pixel resolution;
- band count and data type;
- NoData value when present.

By default, partial edge tiles are skipped, matching the behavior of the original `clip_merge_picture.py` script. Use `--include-partial` if you want edge tiles for rasters whose width or height is not divisible by the tile size.

### GeoTIFF Stitching

The stitching code reads tile positions from filenames and writes a single GeoTIFF mosaic. It supports:

- modern tile names: `image_r0000_c0000.tif`;
- legacy tile names from the original script: `image_0_0.tif`.

The stitcher verifies that the tile grid is complete and that tile CRS, band count, dtype, and NoData metadata are compatible.

### Image Rotation Helper

`DataEnhancement.py` originally rotated common image files such as `.png`. That function is still available as `data_process.augmentation.rotate` and through the CLI. It is a pixel-level OpenCV operation and does not preserve GeoTIFF geospatial metadata.

## Installation

Python 3.8 or newer is recommended.

```bash
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

If you prefer a requirements file:

```bash
python -m pip install -r requirements.txt
```

## Command Line Usage

After installation, use the `data-process` command.

### Split a GeoTIFF

```bash
data-process tile input.tif tiles/ --tile-width 1024 --tile-height 1024
```

Write partial edge tiles:

```bash
data-process tile input.tif tiles/ --tile-width 1024 --tile-height 1024 --include-partial
```

### Stitch Tiles

```bash
data-process stitch tiles/ stitched.tif --overwrite
```

If the nominal tile size cannot be inferred from the top-left tile, pass it explicitly:

```bash
data-process stitch tiles/ stitched.tif --tile-width 1024 --tile-height 1024
```

### Rotate Regular Images

```bash
data-process rotate images/ --rotation 30 --picture-type .png
```

## Python API

```python
from data_process import stitch_geotiff_tiles, tile_geotiff

tiles = tile_geotiff(
    "input.tif",
    "tiles",
    tile_width=1024,
    tile_height=1024,
    full_tiles_only=True,
)

stitch_geotiff_tiles("tiles", "stitched.tif", overwrite=True)
```

## Legacy Script Compatibility

The original function names remain available:

```python
from clip_merge_picture import clip_one_picture, merge_picture

clip_one_picture("./input/origin/test", "2015_rgbn.tif", 1024, 1024)
merge_picture("./input/origin/test/crop1024_1024")
```

New projects should use the package API or CLI instead.

## Minimal Example

Run the example below to generate a small synthetic GeoTIFF, split it into tiles, stitch it back, and verify that image data and spatial metadata are preserved.

```bash
python examples/minimal_geotiff_roundtrip.py
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned maintenance and feature work, including overlap tiles, Cloud Optimized GeoTIFF workflows, metadata validation, and better large-raster performance.

## Project Structure

```text
remote-sensing-raster-tools/
  data_process/
    raster.py          # GeoTIFF tiling and stitching
    augmentation.py    # OpenCV image rotation helper
    cli.py             # command line interface
  examples/
    minimal_geotiff_roundtrip.py
  tests/
    test_raster_processing.py
  clip_merge_picture.py   # legacy compatibility wrapper
  DataEnhancement.py      # legacy compatibility wrapper
```

## Important Limitations

- The tool currently handles GeoTIFF tiling and stitching. It does not implement reprojection, resampling, cloud masking, radiometric correction, dataset cataloging, or machine learning preprocessing pipelines.
- The default tiling mode drops partial edge tiles for compatibility with the original code. Use `--include-partial` when full coverage is needed.
- Stitching expects filenames that encode row and column positions.

## 中文说明

本项目用于遥感影像、卫星影像和航空影像的基础栅格数据处理。当前核心功能是 GeoTIFF 裁剪切片与拼接，并在测试中验证了裁剪后再拼接可以恢复原始影像数据、坐标系、仿射变换、分辨率和 NoData 信息。

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
