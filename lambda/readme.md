## lambda/

AWS Lambda function written in python.  Local development and deployment environment.

### Virtual Environment

Using virtual environments for Python development avoid modify packages associated with the native installation.  Requirement files can be shared and environments can be quickly torn down and rebuilt with a few simple commands.

1. Initialize
    
    `python -m venv .\env-37` will create a virtual environment

2. Activate

    `.\env-37\Scripts\activate` will active the environment.  `deactivate` from any location while in the (venv) terminal will terminate the environment session.

    Data persists through the `.\env-` and thus should not be checked it.

3. Install

    `pip install -r requirements-local.txt`  requirements-local.txt includes dependencies for unit testing and IDE integration.  The archive build will use requirements.txt

### Build &amp; Deploy

#### cfn-launch.sh

Shell script used as the container ENTRYPOINT to `pip install` requirements and create the .zip deployment. See [Dockerfile](../Dockerfile)

#### `src/`

##### `cfn-launch.py`

Script to launch of Cloudformation using Python SDK (boto3).  Contains entrypoint for local development testing and AWS Lambda event handler

- local development makes use of argparse.  `argparse -h` will detail program arguments.  E.g.,

    `py .\lambda\src\cfn_launch.py -h`

    cfn_launch.py takes positional argument used as the stack name during local development.  E.g.,

    `py .\lambda\src\cfn_launch.py my-stack-name`

- The lambda_handler function is here as well.

##### `cfn.py`

A module containing functions to support cfn_launch.py

#### `tests/`

Unit tests against `src/`.

Testcases are created with the intent of being executed from the root directory.  Running `pytest` will scan for available tests and execute.

#### `build/`

The output directory when the builder container completes.

The Dockerfile section on the main page describes the build process.


##### TODO

- `moto` to mock test create_stack