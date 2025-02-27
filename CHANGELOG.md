# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2025-02-27

### Added

- Part revision property.

### Changed

- Location of theme switcher to top navbar.
- Available navigation menu items when in locked state.
- Changed results in both Manual and Automatic modes to
  only show the measurement results.

## [0.0.2] - 2025-02-25

### Added

- Missing API (v1) command for protocol LIST.
- Archive URL parameter in settings endpoint. 
- Precision parameter for measurements.
- Missing MANIFEST file, resulting in broken a Docker
  image.

### Fixed

- Dynamic page resizing for tables with many columns.

## Removed

- Non-function "retry" parameter for phases.

## [0.0.1] - 2025-02-21

### Added

- Command, instrument, measurement, part, phase and 
  protocol endpoints.
- Automated and manual test endpoints. 
- Basic authentication-base lock/unlock functionality.
- Archival client hooks (i.e. TofuPilot)
- JSON web token (JWT) tools for command line and 
  browser.

[0.0.1]: https://github.com/mcpcpc/uhtf/releases/tag/0.0.1
[0.0.2]: https://github.com/mcpcpc/uhtf/releases/tag/0.0.2
[0.0.3]: https://github.com/mcpcpc/uhtf/releases/tag/0.0.3
