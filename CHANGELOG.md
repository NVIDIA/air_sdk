# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.19.0] - 2025-04-22
-   Added new methods to the breakouts endpoint and added tests

## [2.18.0] - 2025-04-17
-   Added fleets endpoint to SDK v2 client 

## [2.17.0] - 2025-04-03
### Air SDK V2 
-   Added manifest endpoint CRUD to SDK v2 client
-   Added simulation v2 control methods
-   Added Topology Parser in SDK-V2
-   Added new methods to images endpoint
-   Added link endpoint CRUD to SDK v2 client and added tests

## [2.16.0] - 2024-10-28
- Added support for `bulk_update_state` on `SimulationNodeViewSet`

## [2.15.0] - 2024-10-23
- Added support for JSON export

## [2.14.0] - 2024-09-19
- Added support for JSON import
- Fixed an issue related to the expected status code when calling `Worker.register()`

## [2.13.0] - 2024-08-26
- Added support for API V2 endpoints

## [2.12.1] - 2024-07-11
- Fixed a bug when calling `capacity.get()` when the returned capacity was `0`

## [2.12.0] - 2024-05-21
- Added support for IB cluster based simulations

## [2.11.0] - 2024-04-30
- Added cloud init support

## [2.10.1] - 2024-04-11
- Increased default read timeout for `Image` uploads

## [2.10.0] - 2024-04-01
### Changed
- All model `update()` calls now generate a `PATCH` request instead of `PUT` to avoid unintentional updates to the object

## [2.9.0] - 2024-03-07
### Added
- All API requests now include an explicit default timeout
- `publish()` and `unpublish()` methods for `Image` objects
### Changed
- Improved 403 error handling

## [2.8.1] - 2024-02-01
### Fixed
- `AirApi.images.create()` now logs an error and still returns the `Image` object when an upload attempt fails

## [2.8.0] - 2024-01-08
### Added
- For sessions authenticated using a username and password, the `AirApi` client instance will now automatically try to refresh its authorization token after it expires

## [2.7.0] - 2024-01-08
### Added
- `AirApi.simulations.create()` now accepts an optional `topology_data` kwarg. This option is now preferred when creating a simulation from a DOT file and assigning it to an organization.
- `AirApi.topologies.create()` now logs a warning when additional kwargs are included with the `dot` kwarg. `AirApi.simulations.create()` should generally be used instead.

## [2.6.0] - 2024-01-04
### Added
- `Organization.create_fleet()` method for creating a private fleet

## [2.5.0] - 2023-12-18
### Changed
- All logs are now generated using a logger named `air_sdk`
### Fixed
- Passwords are redacted from log messages

## [2.4.2] - 2023-11-13
### Added
- Updated required arguments when using the Image API

## [2.4.1] - 2023-11-02
### Added
- Preferences API support
- FleetWorker API support

## [2.4.0] - 2023-04-18
### Added
- `copy()` method for `Image` objects
- ResourceBudget API support

## [2.3.0] - 2022-10-06
### Added
- Organization member management
### Fixed
- Updated `Organization.create()` documentation to reflect Air API changes

## [2.2.0] - 2022-05-27
### Added
- `AirApi.topologies.create()` now accepts an absolute path to a DOT file on the caller's local disk
### Fixed
- `AirModel` objects are now automatically refreshed before calls to `update()`
- Fixed `KeyError` when calling `AirApi.links.list()`

## [2.1.6] - 2022-02-03
### Added
- Marketplace API (thanks @gabrielle9talavera!)
- Token API (thanks @gabrielle9talavera!)

## [2.1.5] - 2021-09-07
### Added
- `datetime` objects are now handled natively by the SDK (#8, thanks @gabrielle9talavera!)

## [2.1.4] - 2021-08-04
### Fixed
- `requests` was missing as a required package for `pip` installs

## [2.1.3] - 2021-07-09
### Fixed
- `_resolve_interface` did not include simulation filter in simulations_interfaces.list() call

## [2.1.2] - 2021-03-08
### Fixed
- `python-dateutil` was missing as a required package for `pip` installs

## [2.1.1] - 2021-03-05
### Changed
- Default API url is now https://air.nvidia.com/api/
### Fixed
- Lazy loading of simulation `services` list

## [2.1.0] - 2021-02-26
### Added
- A warning will now be logged when simulations are created with `expires_at`/`sleep_at` dates in the past
- `AirApi.Simulation.load()` (an alias for `AirApi.Simulation.start()`)
- `AirApi.Simulation.stop()` (an alias for `AirApi.Simulation.store()`)
### Fixed
- `JSONDecodeError` raised when deleting simulation node instructions

## [2.0.4] - 2021-02-10
### Fixed
- LazyLoading some objects caused unwanted `PATCH` calls

## [2.0.3] - 2021-02-08
### Fixed
- Exception thrown when calling `update()` on a newly created `Topology` object

## [2.0.2] - 2021-02-02
### Fixed
- Exception thrown when calling `create_instructions()` on a `SimulationNode` object (!3, thanks @taka.mura!)

## [2.0.1] - 2021-02-01
### Fixed
- `AirApi.simulations.duplicate()` was incorrectly treating a JSON object as a HTTP response (!2, thanks @taka.mura!)
- `AirApi.simulations.duplicate()` did not work when passing in a `Simulation` object (#2)

## [2.0.0] - 2021-01-21
This version introduces a number of **BREKAING** changes from 1.x.x versions. Please read the following carefully.
### Added
- Account API
- Demo API
- Image API
- Interface API
- Job API
- Link API
- Login API
- Organization API
- SSHKey API
- `SimulationNode.create_instructions()`, `SimulationNode.list_instructions()`, and `SimulationNode.delete_instructions()`
- `SimulationNode.control()` and related methods
- All `get()` and `list()` methods now support optional kwargs that are applied as filters to the `GET` request
- All objects now support a `refresh()` method to sync local instances with the API
- AirApi objects now have a `username` attribute when authorized:
```
air = AirApi(bearer_token='foo')
air.username
# mrobertson@nvidia.com
```
### Changed
- Instantiating an AirApi instance now requires a username/password or (pre-generated) bearer token
```
# v1
air = AirApi()

# v2
air = AirApi(username='username', password='<password>')
# or
air = AirApi(bearer_token='<token>')
```
- AirApi instances are now automatically authorized on creation. It is no longer required to call `AirApi.authorize()` separately.
```
# v1
air = AirApi()
air.authorize(username='username', password='<password>')

# v2
air = AirApi(username='<username>', password='<password>')
```
- Updating a local object property now immediately makes a `PATCH` call to update the remote object as well. Multiple properties can still be updated via a `PUT` call with the object's `update()` method.
```
# v1
# only updates the local object, no API calls are made
simulation.title = 'new title'
# updates the remote object with a PUT call
simulation.update(title='new title', name='mrobertson@nvidia.com')

# v2
# immediately updates the remote object with a PATCH call
simulation.title = 'new title'
# updates the remote object with a PUT call
simulation.update(title='new title', name='mrobertson@nvidia.com')
```
*Note:* If multiple properties need to be updated, it is recommended to make a single call to `update()` for efficiency's sake:
```
# DO
simulation.update(title='new title', name='mrobertson@nvidia.com') # PUT #1

# DON'T
simulation.title = 'new title' # PATCH #1
simulation.name = 'mrobertson@nvidia.com' # PATCH #2
```
- The following deprecated methods no longer return a tuple of the created object and the `POST` response JSON. Instead, use `new_object.__dict__` or `new_object.json()`.
    - `PermissionApi.create_permission()`
    - `ServiceApi.create_service()`
    - `SimulationApi.create_simulation()`
    - `TopologyApi.create_topology()`
```
# v1
simulation, payload = air.simulation.create_simulation(topology=topology_id)

# v2
simulation = air.simulations.create(topology=topology)
simulation.__dict__
simulation.json()
```
- The following deprecated methods no longer return a list of dicts. Instead, they return a list of AIR objects.
    - `NodeApi.get_nodes()`
    - `ServiceApi.get_services()`
    - `SimulationApi.get_simulations()`
    - `SimulationInterfaceApi.get_simulation_interfaces()`
    - `SimulationNodeApi.get_simulation_nodes()`
    - `TopologyApi.get_topologies()`
```
# v1
air.simulation.get_simulations()
# [{...}, ...]

# v2
air.simulations.list()
[<Simulation>, ...]
```
- The following methods now return the created `Permission` object (previously they returned `None`)
    - `Simulation.add_permission()`
    - `Topology.add_permission()`
- Any method arguments that represent an AIR object will now accept an instance of that object or its `id` as a string
- All methods that make API calls should now raise `AirUnexpectedResponse` if any non-success response is received
- All methods that make API calls should now raise `AirUnexpectedResponse` if any unexpected response format is received
### Deprecated
- The following methods have been deprecated in favor of a more standard naming convention. These methods will still work in this release (logging a deprecation warning) but will be removed in a future release.
    - `CapacityApi.get_capacity()` is now `CapacityApi.get()`
    - `NodeApi.get_nodes()` is now `NodeApi.list()`
    - `PermissionApi.create_permission()` is now `PermissionApi.create()`
    - `ServiceApi.create_service()` is now `ServiceApi.create()`
    - `ServiceApi.get_services()` is now `ServiceApi.list()`
    - `ServiceApi.get_service()` is now `ServiceApi.get()`
    - `SimulationApi.control()` is now `Simulation.control()`
    - `SimulationApi.create_simulation()` is now `SimulationApi.create()`
    - `SimulationApi.get_simulations()` is now `SimulationApi.list()`
    - `SimulationApi.get_simulation()` is now `SimulationApi.get()`
    - `SimulationApi.update_simulation()` is now `Simulation.update()`
    - `SimulationInterfaceApi.get_simulation_interfaces()` is now `SimulationInterfaceApi.list()`
    - `SimulationNodeApi.get_simulation_nodes()` is now `SimulationNodeApi.list()`
    - `SimulationNodeApi.update_simulation_node()` is now `SimulationNode.update()`
    - `TopologyApi.create_topology()` is now `TopologyApi.create()`
    - `TopologyApi.get_topologies()` is now `TopologyApi.list()`
    - `TopologyApi.update_topology()` is now `Topology.update()`
    - `WorkerApi.get_workers()` is now `WorkerApi.list()`
    - `Worker.set_available()` is now `worker.available = <True|False>`
    - `WorkerApi.update_worker()` is now `Worker.update()`
```
# v1
air.simulation.get_simulations()

# v2
air.simulations.list()
```
- The following properties have been deprecated in favor of a more standard naming convention. These properties will still be available this release (logging a deprecation warning) but will be removed in a future release.
    - `AirApi.node` is now `AirApi.nodes`
    - `AirApi.permission` is now `AirApi.permissions`
    - `AirApi.service` is now `AirApi.services`
    - `AirApi.simulation` is now `AirApi.simulations`
    - `AirApi.simulation_interface` is now `AirApi.simulation_interfaces`
    - `AirApi.simulation_node` is now `AirApi.simulation_nodes`
    - `AirApi.topology` is now `AirApi.topologies`
    - `AirApi.worker` is now `AirApi.workers`
```
# v1
air.simulation

# v2
air.simulations
```

## [1.3.3] - 2020-11-04
### Added
- 403 responses now raise AirForbiddenError

## [1.3.2] - 2020-10-29
### Added
- `host` key to Service

## [1.3.1] - 2020-10-28
### Fixed
- Malformed request payload when using `worker.update_worker()`

## [1.3.0] - 2020-10-22
### Added
- Capacity API
- Worker API
- `SimulationApi.get_citc_simulation()`

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
