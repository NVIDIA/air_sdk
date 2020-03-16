# cumulus_air_sdk

This project provides a Python SDK for interacting with the Cumulus AIR API (https://air.cumulusnetworks.com/api/).

## Installation

pip3 install git+https://gitlab.com/cumulus-consulting/air/cumulus_air_sdk.git

## Usage

```
>>> from air_sdk import AirApi
>>> air = AirApi()
```

Using the API requires the use of either a bearer token or a username/password.

### Bearer token

To use a bearer token, the calling user must have a cumulusnetworks.com account and have previously approved access for Cumulus AIR. Once a token is obtained:

```
>>> air.authorize(token='<token>')
```

### Username/Password

To use a username/password, an administrator of Cumulus AIR must provision a service account. Once the administrator provides the username and password:

```
>>> air.authorize(username='<username>', password='<password>')
```

### Interacting with the API

The SDK provides various helper methods for interacting with the API. For example:

```
>>> air.simulation.get_simulations()
[{'url': 'https://air.cumulusnetworks.com/api/v1/simulation/30364946-99a1-4f1f-b330-ebc95c7d93bb/', 'id': '30364946-99a1-4f1f-b330-ebc95c7d93bb', 'topology': 'https://air.cumulusnetworks.com/api/v1/topology/9ccaa421-3472-4919-a653-10088dfe223a/', 'state': 'SNAPSHOT', 'nodes': ['https://air.cumulusnetworks.com/api/v1/simulation-node/a4f66942-7c28-459a-a2fe-71b6cd43e91f/'], 'services': [], 'name': 'mrobertson@cumulusnetworks.com', 'expires': False, 'expires_at': '2020-03-13T14:40:16.096119Z', 'sleep': True, 'sleep_at': '2020-03-11T02:42:42.001249Z', 'netq_username': None, 'netq_password': None}, {'url': 'https://air.cumulusnetworks.com/api/v1/simulation/47997aff-e08c-4413-b2e7-a37fd1a7848e/', 'id': '47997aff-e08c-4413-b2e7-a37fd1a7848e', 'topology': 'https://air.cumulusnetworks.com/api/v1/topology/9ccaa421-3472-4919-a653-10088dfe223a/', 'state': 'STORED', 'nodes': ['https://air.cumulusnetworks.com/api/v1/simulation-node/c272035d-9592-47d0-b9e3-ef14f07bda13/'], 'services': ['https://air.cumulusnetworks.com/api/v1/service/df1fb45f-2689-4b43-9155-8fe39a09e79c/'], 'name': 'mrobertson@cumulusnetworks.com', 'expires': False, 'expires_at': '2020-03-15T17:07:41.802087Z', 'sleep': True, 'sleep_at': '2020-03-13T09:54:30.489288Z', 'netq_username': 'mrobertson@cumulusnetworks.com', 'netq_password': 'foo'}]
```

## Developing

Contributions to the SDK are very welcome. All code must pass linting and unit testing before it will be merged.

### Requirements

```
pip3 install -r requirements-dev.txt
```

### Linting

```
pylint air_sdk
```

### Unit testing

```
./unit_test.sh
```
