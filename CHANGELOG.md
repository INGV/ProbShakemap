# Changelog

## ProbShakemap 1.3.0

### Added

- Added a packaged Norcia example under `example/norcia`, including input files, example output figures, and a dedicated `run_code.sh`.

### Changed

* Removed the previous (unused) parallelization and kept the calculations serial
* Removed repeated parameter loading
* Solved minor bug in POIs sharing
* Clarified POI subset handling:
    * --pois_subset extracts a new subset and saves it to OUTPUT/POIs.txt
    * --reuse_pois_subset reuses an existing OUTPUT/POIs.txt
    * without any flag, the full POI grid from --pois_file is used
* Improved log messages and functions helper
* Updated GMPE filtering for spectral acceleration periods (added explicit error when selected GMPEs do not support the requested IMT)
* Updated README

### Fixed

- Fixed POI subset sharing so reuse fails with a clear error if `OUTPUT/POIs.txt` is missing
- Avoided recalculating statistics repeatedly by caching computed statistics

