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


### Local development

### `cfn-launch.py`

Script the launching of Cloudformation through the Python SDK (boto3).  Contains entrypoint for local development testing and AWS Lambda event handler

### cfn-launch.sh

The shell script used as the container ENTRYPOINT to `pip install` requirements and create the .zip deployment.

### `src/`

Source files for local development and lambda.

### `test/`

Unit tests against `src/`

### `build/`

### TODO

- TODO research `moto` to mock test create_stack