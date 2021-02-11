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

    cfn_launch.py takes on positional argument required for the stack name during local development.  E.g.,

    `py .\lambda\src\cfn_launch.py my-stack-name`

- The lambda_handler function is here as well.  The lambda handler will use the S3 object event prefix as the stack name.

##### `cfn.py`

A module containing functions to support cfn_launch.py

#### `tests/`

Unit tests against `src/`.

Testcases are created with the intent of being executed from the root directory.  Running `pytest` will scan for available tests and execute.

#### `build/`

The output directory when the builder container completes.

The Dockerfile section on the main page describes the build process.

#### S3 Policy
This policy resource is intentionally permissive and should be further refined at the point of implementation.

#### S3 Policy
This policy resource is intentionally permissive and should be further refined at the point of implementation.

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucketMultipartUploads",
                    "s3:ListBucketVersions",
                    "s3:ListBucket",
                    "s3:ListMultipartUploadParts",
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::BUCKET_NAME_HERE",
                    "arn:aws:s3:::BUCKET_NAME_HERE/*"
                ]
            }
        ]
    }

#### SSM Policy
This policy resource is intentionally permissive and should be further refined at the point of implementation.

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath"
                ],
                "Resource": [
                    "arn:aws:ssm:us-east-1:ACCOUNT_ID_HERE:parameter/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:PutParameter"
                ],
                "Resource": "arn:aws:ssm:us-east-1:ACCOUNT_ID_HERE:parameter/*"
            }
        ]
    }

#### CloudFormation Policy
This policy resource is intentionally permissive and should be further refined at the point of implementation.

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "cloudformation:ContinueUpdateRollback",
                    "cloudformation:DeregisterType",
                    "cloudformation:ExecuteChangeSet",
                    "cloudformation:RegisterType",
                    "cloudformation:SignalResource",
                    "cloudformation:Delete*",
                    "cloudformation:Set*",
                    "cloudformation:Create*",
                    "cloudformation:Update*",
                    "cloudformation:Stop*",
                    "cloudformation:Cancel*"
                ],
                "Resource": "arn:aws:cloudformation:us-east-1:ACCOUNT_ID_HERE:stack/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "cloudformation:Describe*"
                ],
                "Resource": "arn:aws:cloudformation:us-east-1:ACCOUNT_ID_HERE:stack/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:Describe*",
                    "ec2:RunInstances"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:AddRoleToInstanceProfile",
                    "iam:RemoveRoleFromInstanceProfile",
                    "iam:CreateInstanceProfile",
                    "iam:DeleteInstanceProfile"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:PassRole"
                ],
                "Resource": "arn:aws:iam::ACCOUNT_ID_HERE:role/cfnec2-instance-role"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ses:SendEmail",
                    "ses:SendTemplatedEmail",
                    "ses:SendRawEmail"
                ],
                "Resource": "arn:aws:ses:*:ACCOUNT_ID_HERE:identity/*"
            }
        ]
    }