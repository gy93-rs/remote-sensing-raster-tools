"""Command line interface for data-process."""

from __future__ import annotations

import argparse
from pathlib import Path

from .augmentation import rotate
from .raster import stitch_geotiff_tiles, tile_geotiff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-process",
        description="Tile and stitch GeoTIFF remote sensing imagery.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tile_parser = subparsers.add_parser("tile", help="Split a GeoTIFF into tiles")
    tile_parser.add_argument("input", type=Path, help="Input GeoTIFF")
    tile_parser.add_argument("output_dir", type=Path, help="Directory for output tiles")
    tile_parser.add_argument("--tile-width", type=int, required=True, help="Tile width in pixels")
    tile_parser.add_argument("--tile-height", type=int, required=True, help="Tile height in pixels")
    tile_parser.add_argument("--prefix", help="Output filename prefix; defaults to input stem")
    tile_parser.add_argument(
        "--include-partial",
        action="store_true",
        help="Write partial edge tiles instead of dropping them",
    )
    tile_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing tiles")
    tile_parser.set_defaults(func=_tile_command)

    stitch_parser = subparsers.add_parser("stitch", help="Stitch GeoTIFF tiles")
    stitch_parser.add_argument("tiles_dir", type=Path, help="Directory containing GeoTIFF tiles")
    stitch_parser.add_argument("output", type=Path, help="Output GeoTIFF")
    stitch_parser.add_argument("--tile-width", type=int, help="Nominal tile width in pixels")
    stitch_parser.add_argument("--tile-height", type=int, help="Nominal tile height in pixels")
    stitch_parser.add_argument("--overwrite", action="store_true", help="Overwrite output file")
    stitch_parser.set_defaults(func=_stitch_command)

    rotate_parser = subparsers.add_parser("rotate", help="Rotate regular image files")
    rotate_parser.add_argument("root_path", type=Path, help="Directory containing images")
    rotate_parser.add_argument("--rotation", type=int, required=True, help="Rotation step in degrees")
    rotate_parser.add_argument("--picture-type", required=True, help="File extension, such as .png")
    rotate_parser.set_defaults(func=_rotate_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


def _tile_command(args: argparse.Namespace) -> None:
    tiles = tile_geotiff(
        args.input,
        args.output_dir,
        args.tile_width,
        args.tile_height,
        prefix=args.prefix,
        full_tiles_only=not args.include_partial,
        overwrite=args.overwrite,
    )
    print(f"Wrote {len(tiles)} tile(s) to {args.output_dir}")


def _stitch_command(args: argparse.Namespace) -> None:
    output = stitch_geotiff_tiles(
        args.tiles_dir,
        args.output,
        tile_width=args.tile_width,
        tile_height=args.tile_height,
        overwrite=args.overwrite,
    )
    print(f"Wrote stitched GeoTIFF to {output}")


def _rotate_command(args: argparse.Namespace) -> None:
    outputs = rotate(args.root_path, args.rotation, args.picture_type)
    print(f"Wrote {len(outputs)} rotated image(s)")


if __name__ == "__main__":
    raise SystemExit(main())
