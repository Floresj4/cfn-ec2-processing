## lambda/

A python AWS Lambda function triggered from a S3 object creation event.

Developing in a virtual environment is always a good idea.  

`python -m venv .\env-37` will create a virtual environment to avoid overwriting dependencies on your local python installation

`env-*/` is listed in the root .gitignore

The 

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