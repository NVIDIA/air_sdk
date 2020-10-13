# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.3] - 2020-10-13
### Fixed
- `Simulation.create_service()` now returns the newly created `Service` object

## [1.2.2] - 2020-10-12
### Added
- `simulation.get_simulation()`
- `service.get_service()`
- `Simulation.services` now contains `Service` objects

## [1.2.1] - 2020-10-09
### Added
- `store()` and `delete()` methods for a simulation

## [1.2.0] - 2020-09-21
### Added
- Topology API
- `create_simulation()`
- `start()` method for simulations
- SimulationNode API

## [1.1.3] - 2020-06-29
### Added
- `status_code` attribute for `AirError`

## [1.1.2] - 2020-04-22
### Added
- kwargs for simulation.duplicate()

## [1.1.1] - 2020-04-01
### Fixed
#1: AirApi should default to production AIR URL

## [1.1.0] - 2020-03-17
### Added
- Simulation: methods for duplicating sims, adding services, adding permissions
- Added Node
- Added Permission
- Added Service
- Added SimulationInterface
- Added util functions

## [1.0.0] - 2020-03-16
### Added
- Initial functionality
