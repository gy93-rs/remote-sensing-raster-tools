# Roadmap

This roadmap focuses on making `remote-sensing-raster-tools` more useful and maintainable for remote sensing, satellite imagery, and aerial imagery workflows.

## Near Term

- Add tile overlap support for machine learning and visual inspection workflows.
- Improve partial edge tile documentation and examples.
- Add metadata validation commands that report CRS, transform, resolution, band count, dtype, and NoData consistency before stitching.
- Add issue templates for bug reports, feature requests, and geospatial metadata problems.
- Add a pull request template that guides contributors through tests and metadata checks.

## Medium Term

- Add Cloud Optimized GeoTIFF friendly read/write options.
- Add large-raster performance benchmarks using synthetic rasters.
- Support tile manifests so stitching does not depend only on filenames.
- Add optional compression and tiling profile controls for output GeoTIFFs.
- Add richer CLI examples for satellite and aerial imagery preprocessing.

## Longer Term

- Explore vector AOI based clipping when a clear, well-tested API can be added.
- Explore packaging and release automation after the API stabilizes.
- Expand test coverage for multi-band rasters, NoData-heavy rasters, and mixed tile grids.
- Document maintainer workflows for reviewing geospatial metadata changes.

## How Codex Can Help

Codex can help maintain this project by generating tests for edge cases, reviewing pull requests for metadata regressions, improving documentation, and accelerating implementation of focused raster processing features without turning the project into an overbroad remote sensing platform.
