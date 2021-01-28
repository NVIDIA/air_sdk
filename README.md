# cumulus_air_sdk

This project provides a Python SDK for interacting with the Cumulus AIR API (https://air.cumulusnetworks.com/api/).

[Click here for the full documentation](https://cumulus-consulting.gitlab.io/air/cumulus_air_sdk/docs/)

## Installation

The SDK requires python 3.6 or later. To install:

```
pip3 install git+https://gitlab.com/cumulus-consulting/air/cumulus_air_sdk.git
```

## Usage

```
>>> from air_sdk import AirApi
>>> air = AirApi(username='<user>', password='<password>')
```

## Authentication Options

Using the API requires the use of either a bearer token or a username/password.

### Bearer token

To use a bearer token, the calling user must have a cumulusnetworks.com account and have previously approved access for Cumulus AIR. Once a token is obtained:

```
>>> air = AirApi(bearer_token='<token>')
```

### Username/Password

To use a username/password, an administrator of Cumulus AIR must provision a service account. Once the administrator provides the username and password:

```
>>> air = AirApi(username='<user>', password='<password>')
```

### Interacting with the API

The SDK provides various helper methods for interacting with the API. For example:

```
>>> air.simulations.list()
[<Simulation sim1 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Simulation sim2 3134711d-015e-49fb-a6ca-68248a8d4aff>]
>>> sim1 = air.simulations.get('c51b49b6-94a7-4c93-950c-e7fa4883591')
>>> sim1.title = 'My Sim'
>>> sim1.store()
```

## Developing

Contributions to the SDK are very welcome. All code must pass linting and unit testing before it will be merged.

### Requirements

```
pip3 install -r requirements-dev.txt
```

### Linting

```
pylint **/*.py
```

### Unit testing

```
./unit_test.sh
```
