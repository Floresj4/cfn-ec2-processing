# Data Processing w/ Cloudformation and EC2

An exploratory project to launch an EC2 instance and begin a batch processing job based on some trigger event.

Objectives
 - A new release of the batch component will trigger processing
 - Options to the processing event can be externalized and easily mananged between events

## cfn-launch.py

Script the launching of Cloudformation through the Python SDK (boto3).  This script allows testing stack creation outside of the AWS Cloudformation Wizard.  This code will ultimately be executed via AWS Lambda or a container in AWS CodePipeline.