# Changelog

## ProbShakemap 1.3.0

### Changed

- Removed the previous (unused) parallelization and kept the calculations serial
- Removed repeated parameter loading
- Solved minor bug in POIs sharing
- Clarified POI subset handling:
  - `--pois_subset` extracts a new subset and saves it to `OUTPUT/POIs.txt`
  - `--reuse_pois_subset` reuses an existing `OUTPUT/POIs.txt`
  - without any flag, the full POI grid from `--pois_file` is used
- Updated the GitHub example run script (/example/norcia)

