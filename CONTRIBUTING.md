# Contributing

Thank you for helping improve `data_process`.

## Development Setup

```bash
python -m pip install -e ".[test]"
pytest
```

## Pull Request Guidelines

- Keep changes focused and explain the remote sensing workflow they support.
- Add or update tests for GeoTIFF metadata behavior when changing tiling or stitching.
- Do not commit private imagery, credentials, tokens, or large generated outputs.
- Prefer small synthetic rasters in tests instead of real satellite or aerial images.
- Document command line changes in `README.md`.

## Code Style

- Use clear Python type hints where they make behavior easier to understand.
- Preserve CRS, transform, resolution, dtype, band count, and NoData metadata for GeoTIFF operations.
- Avoid hard-coded local paths.
