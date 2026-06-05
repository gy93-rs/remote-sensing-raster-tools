"""GeoTIFF tiling and stitching utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import rasterio
from rasterio.windows import Window


_MODERN_TILE_RE = re.compile(r"_r(?P<row>\d+)_c(?P<col>\d+)\.tif{1,2}$", re.IGNORECASE)
_LEGACY_TILE_RE = re.compile(r"_(?P<row>\d+)_(?P<col>\d+)\.tif{1,2}$", re.IGNORECASE)


@dataclass(frozen=True)
class TileInfo:
    """A generated or discovered raster tile."""

    path: Path
    row: int
    col: int
    width: int
    height: int


def tile_geotiff(
    input_path: str | Path,
    output_dir: str | Path,
    tile_width: int,
    tile_height: int,
    *,
    prefix: str | None = None,
    full_tiles_only: bool = True,
    overwrite: bool = False,
    legacy_names: bool = False,
) -> list[TileInfo]:
    """Split a GeoTIFF into non-overlapping tiles.

    The output tiles preserve the source CRS, dtype, band count, nodata value,
    resolution, and per-tile affine transform. By default, partial edge tiles
    are skipped to match the behavior of the original script.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    _validate_tile_size(tile_width, tile_height)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[TileInfo] = []
    with rasterio.open(input_path) as src:
        tile_prefix = prefix or input_path.stem
        row_index = 0
        for row_off in range(0, src.height, tile_height):
            window_height = min(tile_height, src.height - row_off)
            if full_tiles_only and window_height < tile_height:
                continue
            col_index = 0
            for col_off in range(0, src.width, tile_width):
                window_width = min(tile_width, src.width - col_off)
                if full_tiles_only and window_width < tile_width:
                    continue

                output_path = output_dir / _tile_name(
                    tile_prefix, row_index, col_index, legacy_names=legacy_names
                )
                if output_path.exists() and not overwrite:
                    raise FileExistsError(f"Tile already exists: {output_path}")

                window = Window(col_off, row_off, window_width, window_height)
                profile = src.profile.copy()
                profile.update(
                    height=window_height,
                    width=window_width,
                    transform=src.window_transform(window),
                )

                with rasterio.open(output_path, "w", **profile) as dst:
                    dst.write(src.read(window=window))

                written.append(
                    TileInfo(
                        path=output_path,
                        row=row_index,
                        col=col_index,
                        width=window_width,
                        height=window_height,
                    )
                )
                col_index += 1
            row_index += 1

    return written


def stitch_geotiff_tiles(
    tiles_dir: str | Path,
    output_path: str | Path,
    *,
    tile_width: int | None = None,
    tile_height: int | None = None,
    overwrite: bool = False,
) -> Path:
    """Stitch GeoTIFF tiles created by :func:`tile_geotiff`.

    Tile positions are read from filenames. Both the modern
    ``name_r0000_c0000.tif`` convention and the legacy ``name_0_0.tif``
    convention are supported.
    """

    tiles_dir = Path(tiles_dir)
    output_path = Path(output_path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output_path}")

    resolved_output = output_path.resolve()
    tile_paths = [
        path
        for path in sorted(tiles_dir.glob("*.tif")) + sorted(tiles_dir.glob("*.tiff"))
        if path.resolve() != resolved_output
    ]
    if not tile_paths:
        raise FileNotFoundError(f"No GeoTIFF tiles found in {tiles_dir}")

    opened = []
    try:
        for path in tile_paths:
            row, col = _parse_tile_position(path)
            src = rasterio.open(path)
            opened.append((path, row, col, src))

        top_left = _find_top_left_tile(opened)
        nominal_width = tile_width or top_left.width
        nominal_height = tile_height or top_left.height
        _validate_tile_size(nominal_width, nominal_height)
        _validate_grid(opened)
        _validate_compatible_profiles(opened)

        output_width = max(col * nominal_width + src.width for _, _, col, src in opened)
        output_height = max(row * nominal_height + src.height for _, row, _, src in opened)
        profile = top_left.profile.copy()
        profile.update(
            width=output_width,
            height=output_height,
            transform=top_left.transform,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, "w", **profile) as dst:
            for _, row, col, src in opened:
                dst.write(
                    src.read(),
                    window=Window(
                        col * nominal_width,
                        row * nominal_height,
                        src.width,
                        src.height,
                    ),
                )
    finally:
        for _, _, _, src in opened:
            src.close()

    return output_path


def _validate_tile_size(tile_width: int, tile_height: int) -> None:
    if tile_width <= 0 or tile_height <= 0:
        raise ValueError("tile_width and tile_height must be positive integers")


def _tile_name(prefix: str, row: int, col: int, *, legacy_names: bool) -> str:
    if legacy_names:
        return f"{prefix}_{row}_{col}.tif"
    return f"{prefix}_r{row:04d}_c{col:04d}.tif"


def _parse_tile_position(path: Path) -> tuple[int, int]:
    for pattern in (_MODERN_TILE_RE, _LEGACY_TILE_RE):
        match = pattern.search(path.name)
        if match:
            return int(match.group("row")), int(match.group("col"))
    raise ValueError(
        f"Cannot read tile row/column from {path.name}; expected *_r0000_c0000.tif "
        "or legacy *_0_0.tif naming"
    )


def _find_top_left_tile(opened: Iterable[tuple[Path, int, int, rasterio.io.DatasetReader]]):
    for _, row, col, src in opened:
        if row == 0 and col == 0:
            return src
    raise ValueError("Tile grid must include row 0, column 0")


def _validate_grid(opened: list[tuple[Path, int, int, rasterio.io.DatasetReader]]) -> None:
    positions = {(row, col) for _, row, col, _ in opened}
    max_row = max(row for _, row, _, _ in opened)
    max_col = max(col for _, _, col, _ in opened)
    missing = [
        (row, col)
        for row in range(max_row + 1)
        for col in range(max_col + 1)
        if (row, col) not in positions
    ]
    if missing:
        preview = ", ".join(f"r{row}c{col}" for row, col in missing[:5])
        raise ValueError(f"Tile grid is incomplete; missing {preview}")


def _validate_compatible_profiles(
    opened: list[tuple[Path, int, int, rasterio.io.DatasetReader]]
) -> None:
    first_path, _, _, first = opened[0]
    for path, _, _, src in opened[1:]:
        if src.count != first.count:
            raise ValueError(f"{path} has {src.count} bands; expected {first.count}")
        if src.dtypes != first.dtypes:
            raise ValueError(f"{path} has dtype {src.dtypes}; expected {first.dtypes}")
        if src.crs != first.crs:
            raise ValueError(f"{path} CRS differs from {first_path}")
        if src.nodata != first.nodata:
            raise ValueError(f"{path} nodata differs from {first_path}")
