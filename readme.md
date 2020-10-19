# Data Processing w/ Cloudformation and EC2

An exploratory project to launch an EC2 instance and begin a batch processing job based on some trigger event.

Objectives
 - A new release of the batch component will trigger processing
 - Options to the processing event can be externalized and easily mananged between events

## cfn-launch.py

Script the launching of Cloudformation through the Python SDK (boto3).  This script allows testing stack creation outside of the AWS Cloudformation Wizard.  This code will ultimately be executed via AWS Lambda or a container in AWS CodePipeline.

### parameters.yml

Parameters.yaml is a configuration file used with the cloudformation client to substitute values that would have otherwise been manually entered via the AWS Cloudformation Wizard.  This file is loaded from the `./cloudformation` directory.  The list of required parameters is found in the Parameters section of `./cloudformation/template.yml`.
