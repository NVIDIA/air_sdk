---
menu: main
product: AIR SDK
title: AirApi
---

# Table of Contents

* [air\_sdk.air\_api](#air_sdk.air_api)
  * [AirApi](#air_sdk.air_api.AirApi)
    * [\_\_init\_\_](#air_sdk.air_api.AirApi.__init__)
    * [authorize](#air_sdk.air_api.AirApi.authorize)
    * [get\_token](#air_sdk.air_api.AirApi.get_token)
    * [get](#air_sdk.air_api.AirApi.get)
    * [post](#air_sdk.air_api.AirApi.post)
    * [put](#air_sdk.air_api.AirApi.put)
    * [patch](#air_sdk.air_api.AirApi.patch)
    * [delete](#air_sdk.air_api.AirApi.delete)

Cumulus AIR API module

<a name="air_sdk.air_api.AirApi"></a>
## AirApi

Main interface for an API client instance

<a name="air_sdk.air_api.AirApi.__init__"></a>
### \_\_init\_\_

Create a new API client instance. The caller MUST provide either `username` and `password`
or a `bearer_token`

**Arguments**:

- `username` _str, optional_ - Username
- `password` _str, optional_ - Password
- `bearer_token` _str, optional_ - Pre-generated bearer token
- `api_url` _str, optional_ - Default = https://air.cumulusnetworks.com/api/
- `api_version` _str_ - Default = v1

<a name="air_sdk.air_api.AirApi.authorize"></a>
### authorize

Authorizes the API client using either a pre-generated bearer token or a username/password.
Callers MUST pass either a valid `bearer_token` or a `username` and `password`.
After successfully authorizing, all subsequent API calls will include the
authorization token provided by the AIR API. **Note:** This is called once automatically
when an AirApi object is instantiated.

**Arguments**:

- `bearer_token` _str, optional_ - Pre-generated bearer token
- `username` _str, optional_ - Username
- `password` _str, optional_ - Password
  

**Raises**:

  ValueError - Caller did not pass either a token or a username/password

<a name="air_sdk.air_api.AirApi.get_token"></a>
### get\_token

Gets a new bearer token for a given username and password

**Arguments**:

- `username` _str_ - Username
- `password` _str_ - Password
  

**Returns**:

- `str` - Bearer token
  

**Raises**:

  - [`AirAuthorizationError`](/docs/exceptions) - API did not return a token
  - `JSONDecodeError` - API's response is not a valid JSON object

<a name="air_sdk.air_api.AirApi.get"></a>
### get

Wrapper method for GET requests

<a name="air_sdk.air_api.AirApi.post"></a>
### post

Wrapper method for POST requests

<a name="air_sdk.air_api.AirApi.put"></a>
### put

Wrapper method for PUT requests

<a name="air_sdk.air_api.AirApi.patch"></a>
### patch

Wrapper method for PATCH requests

<a name="air_sdk.air_api.AirApi.delete"></a>
### delete

Wrapper method for DELETE requests

