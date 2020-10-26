# Data Processing w/ Cloudformation and EC2

An exploratory project to launch an EC2 instance and begin a batch processing job based on some trigger event.

Objectives
 - A new release of the batch component will trigger processing
 - Options to the processing event can be externalized and easily mananged between events

## Folders
[lambda](./lambda/lambda.md) - the lambda function initiating the stack creation event.
[batch-processor](./batch-processor/batch.md)

### cloudformation/

Contains the local testing and development cloudformation templates.  For Lambda execution the contents of these file must exist in a combination of S3 or Parameter Store.

### params.yml

Params.yml is a configuration file used with the cloudformation client to substitute values that would have otherwise been manually entered via the AWS Cloudformation Wizard.  This file is loaded from the `./cloudformation` directory.  The list of required parameters is found in the Parameters section of `./cloudformation/template.yml`.

params.yml is intentional excluded. See [/API_Parameter.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_Parameter.html) for more details

## batch-processor

A Java batch processing project using Spring Batch.

### batch-processor-data

A data file to run through the batch processing project.  This file will be pulled from AWS S3 when the EC2 instance initializes and starts the process.


## Dockerfile

Dockerfile is used to create the lambda deployment archive.  AWS Lambda runs on Linux and there are scenarios where a deployment created on a Windows machine will not run on Linux &ndash; pyopenssl and cryptography at least.

The docker build command will create and tag a container from the current directory.

`docker build -t cfn-launch-lambda .`

The cfn-launch-lambda container is intended to bind mount the root directory and output the .zip deployment to lambda-out/.  Bind mount allows the archive to be recreated without rebuilding the container image.

The `-v` option binds the current directory to `/usr/share/workspace` to pip install all required dependencies.  The workspace/ directory matches the WORKSPACE argument in Dockerfile.

`docker run -v "%CD%":/usr/share/workspace cfn-launch-lambda:latest`

### lambda/cfn-launch.sh

The shell script used as the container ENTRYPOINT to `pip install` requirements and create the .zip deployment.