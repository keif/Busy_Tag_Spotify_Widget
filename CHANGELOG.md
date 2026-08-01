# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [1.0.0] - 2026-08-01

### Added

- Add automatic BusyTag display refresh and improve OAuth flow
- Add automatic LED color extraction from album artwork
- Add BPM-synchronized LED pattern animation
- Add connection lost screen with retry logic

### Documentation

- Update README with LED color extraction feature

### Fixed

- Improve config reliability and add default volume path
- Improve BusyTag display refresh reliability
- Resolve BusyTag remount timeout and improve mount reliability

### Maintenance

- Add Mac OS capability
- Migrate to uv, add CI + Dependabot (#1)
- Add changelog + release automation, unify version


