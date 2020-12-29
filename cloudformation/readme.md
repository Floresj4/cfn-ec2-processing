## cloudformation/

Contains the local testing and development cloudformation templates.  For Lambda execution the contents of these file must exist in a combination of S3 or Parameter Store.

### template.yml

The main cloudformation template for resource creation.

### params.yml

Params.yml is a configuration file used with the cloudformation client to substitute values that would have otherwise been manually entered via the AWS Cloudformation Wizard.  This file is loaded from the `./cloudformation` during local development.  The list of required parameters is found in the Parameters section of `./cloudformation/template.yml`.

params.yml is intentional excluded. See [/API_Parameter.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_Parameter.html) for more details

### InstanceRole

An instance role is required that can interact with S3 objects (downloading data files and the `event-resource` jar) and Parameter Store entries (command line arguments for the application).  

#### S3 Policy

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::BUCKET_NAME_HERE/*"
                ]
            }
        ]
    }

#### SSM Policy

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
            }
        ]
    }