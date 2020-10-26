## lambda/

A python AWS Lambda function triggered from a S3 object creation event.

### `cfn-launch.py`

Script the launching of Cloudformation through the Python SDK (boto3).  Contains entrypoint for local development testing and AWS Lambda event handler

### `cfn.py`

The Python module containing utility functions supporting cfn_launch.py

### `test/`

### `build/`