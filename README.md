# air_sdk

This project provides a Python SDK for interacting with the NVIDIA Air API (https://air.nvidia.com/api/).

[Click here for the full documentation](https://docs.nvidia.com/networking-ethernet-software/guides/nvidia-air/Air-Python-SDK/)

## Prerequisite

The SDK requires python 3.7 or later. The safest way to install the SDK is to set up a virtual environment in python3.7:

```
apt-get install python3.7
```

```
python3.7 -m pip install virtualenv
```

```
python3.7 -m virtualenv venv37
```

```
. venv37/bin/activate
```

## Installation

To install the SDK, use pip:

```
python3 -m pip install air-sdk
```

## Usage

```
>>> from air_sdk import AirApi
>>> air = AirApi(username='<user>', password='<password>')
```

## Authentication Options

Using the API requires the use of either an API token, a username/password, or a bearer token.

### API token

To use an API token, one must first be generated. The easiest way to do this is via the [Air UI](https://air.nvidia.com/settings/api-tokens).

Once a token is generated:

```
>>> air = AirApi(username='<username>', password='<api_token>')
```

### Username/Password

To use a username/password, an administrator of NVIDIA Air must provision a service account. Once the administrator provides the username and password:

```
>>> air = AirApi(username='<username>', password='<password>')
```

### Bearer token

Generally, it's recommended to use an [API Token](#api-token) over a bearer token. However, a bearer token might be used for testing or quick-and-dirty operations that might not need a long term API token. To use a bearer token, the calling user must have a nvidia.com account and have previously approved access for NVIDIA Air. Once a token is obtained:

```
>>> air = AirApi(bearer_token='<bearer_token>')
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
python3 -m pip install .[dev]
```

### Poetry
The Poetry virtual environment manager should be the preferred way to manage and install dependencies of the SDK. General information about Poetry can be found [here.](https://python-poetry.org/docs/) 

In order to use Poetry, you'll need to install poetry on your machine. 
If you're on a MacBook and have `brew` installed, you can easily accomplish this through the following:
```
brew install poetry
```
After Poetry is installed, you can install all dependencies for the project by running the following:
```
poetry install --all-extras
```

### Unit testing

```
./unit_test.sh
```

### Linting

```
ruff check
```

## Pre-commit hooks
In this section, we delineate the usage of pre-commit hooks for this project.   

### Prerequisites
This section assumes that you've already accomplished the following:
1. Cloned the codebase.
2. Have a `.git` configuration file in your local environment (this is where pre-commit will "hook" into git commits).
3. Created a python virtual environment.
4. Activated your virtual environment.
5. Installed all dependencies with `poetry install --all-extras`

If you don't know whether you have accomplished all of the above, try running `pre-commit --version` or `ruff --version` in your terminal at the source directory of the codebase.

### Adding pre-commit to your environment.
In order to use pre-commits, they need to be configured into your `.git` directory. This is accomplished by running the following in your terminal:
```
>>> pre-commit install
pre-commit installed at .git/hooks/pre-commit
>>>
```
And that's it! You should now have pre-commit hooks activated on your local environment. 

If you would like to uninstall your pre-commit hooks, run `pre-commit uninstall`.  
It's important to note that you should NOT run `python3 -m pip uninstall pre-commit` prior to uninstalling pre-commits from your `.git` directory, or else you might be blocked from making commits to your project. 
If this happens, re-install pre-commit with pip, run `pre-commit uninstall`, and then `python3 -m pip uninstall pre-commit`.


#### Working with pre-commit hooks.
Pre-commit hooks work with git to identify files which you've made changes to and then runs specific operations (such as linting or formatting) on those files.

Currently, our primary hooks are performed by `ruff`, a Python linter and formatter. When attempting to git commit a code change is made that doesn't comply with the default `ruff` configuration and our custom configurations outlined in `.ruff.toml`, `ruff` will attempt to resolve the issue automatically by fixing small linting issues and re-formatting your code.  

In cases where the pre-commit hooks cannot safely correct your code, errors will be printed in your console which typically will provide links to the pieces of code you must address in order to successfully commit the code.

In general, the development workflow is identical to what typically occurs when working on the codebase:
1. Write/modify some code.
2. Run `git add .`
3. Run `git commit -m 'Your detailed commit message here.'`

However, prior to successfully executing step 3 above, all pre-commits configured in `.pre-commit-config.yaml` are run. 
If the `ruff` formatting and linting both pass, your commit will be made. Otherwise, you will need to address the issues and re-add/commit your code.
If the linter or formatter end up modifying your code, you will need to `git add .` these changes and commit them as well.


### Information on specific pre-commit hooks we use. 
We currently use the following hooks.

#### [Ruff (linter)](https://docs.astral.sh/ruff/linter/)
Linting is the process of identifying and highlighting syntactical and stylistic trends and issues within code.
This process helps developers identify and correct programming errors or unconventional coding practices.

We use the ruff linter for our linting needs. This is configured in our `.pre-commit-config.yaml` here:
```
# .pre-commit-config.yaml
repos:
    ...
    hooks:
    - id: ruff
        args: [ --fix ]
```
We've included the `--fix` argument, which requests that `ruff` attempt to correct safely fixable issues without asking us ahead of time. Ruff also has an `--unsafe-fixes` flag that we could add to address fixes that are more risky to correct via automation, however we are not using that flag at this time.

To manually run the linter, run `ruff --fix path/to/your/directory/file.py` or `ruff --fix path/to/your/directory`.

If you would like to ignore a linting error on a specific piece of code, add a `# noqa: CODE_TO_IGNORE` tag next to the piece of code:
```
def this_is_fully_linted(*args, **kwargs):
    ...
    
def this_is_fully_linted_except_F841(*args, **kwargs):  # noqa: F841
    ...
```

You can skip the linting of a specific code on entire files by adding `# ruff: noqa: CODE_TO_IGNORE` to the top of the file.
```
# ruff: noqa: F841

def this_will_not_be_linted_for_F841(*args, **kwargs):
    ....
    
def this_also_will_not_be_linted_for_F841(*args, **kwargs):
    ....
```

To skip linting entirely for the entire folder, simply put `# ruff: noqa` at the top of the file. 


#### [Ruff (formatter)](https://docs.astral.sh/ruff/formatter/)
We use ruff for our code formatting needs. 
Formatting is the process of styling existing code so that it abides by a predetermined set of standards. 
This is important when working with large code-bases or when working with other developers since it makes large code-changes more uniform in style and easier to read. 
When code is more readable, it enables developers to identifying errors in their code logic more easily and helps other developers understand your implementation of features when they are reviewing your code.


We use ruff for our code formatting needs. This is configured in our `.pre-commit-config.yaml`  here:
```
# .pre-commit-config.yaml
repos:
    ...
    hooks:
    - id: ruff-format
```
To manually format your code, run `ruff format path/to/your/directory/file.py` or `ruff format path/to/your/directory`.

If you would like to suppress formatting on a section of code, you can wrap your code in `# fmt: off` and `# fmt: on`:
```
# fmt: off
def this_function_will_not_be_formatted(arg1,
    arg2,
    arg3, arg4,
):
    ...
# fmt: on
```
Alternatively, you can add `# fmt: skip` next to a body of code to supress formatting:
```
class ThisClassIsFormatted:
    ...
    
    
class ThisClassIsNotFormatted: # fmt: skip
    ...
```

#### VS Code Extension
There is a `ruff` VS Code extension you may add to your IDE if you are using VS Code. 
Details on this extension can be found [here](https://github.com/astral-sh/ruff-vscode).

We have already configured the ruff linter and formatter as suggested extensions for the project. They can be found in `.vcode/settings.json`.
