import sys, os
import argparse, logging
import json
import uuid

import boto3
from botocore.config import Config

from cfn import CFN
from cfn import initialize_logger

logger = initialize_logger()


'''
lambda entrypoint
'''
def lambda_handler(event, context):
    try:
        cloudform_bucket = os.getenv('CLOUDFORM_BUCKET', None)
        cloudform_key = os.getenv('CLOUDFORM_KEY', None)
        if None in (cloudform_bucket, cloudform_key):
            raise Exception('Cloudformation resources must exist to proceed.')

        # there could be multiple records...
        # stackname will be the object creating the event
        cfn = CFN(cloudform_bucket, cloudform_key)
        bucket, key = cfn.get_event_info(event)

        if not key.endswith('.jar'):
            raise Exception(f'The key {key} is not supported.')

        stack_name = cfn.get_name(key)
        stack_namespace = cfn.get_namespace(bucket, key)

        # fail if no params, especially event-data
        if not cfn.verify_namespace(stack_namespace):
            raise Exception(f'{stack_namespace} exists, but event-data was not found.')

        # put the event resource param for the instance to download
        cfn.put_event_resource_param(stack_namespace, bucket, key)

        # get template, parameters, and userdata
        template_body_str = cfn.get_template_body_as_string()
        template_parameters = cfn.get_template_params_as_yaml()
        instance_userdata = cfn.get_user_data(stack_namespace)

        # append the stack name as the Name tag on the EC2 instance
        template_parameters.extend([
            { 'ParameterKey': 'InstanceName', 'ParameterValue': stack_name },
            { 'ParameterKey': 'InstanceUserData', 'ParameterValue': instance_userdata }
        ])

        # execute the client request to create
        cfn_response = cfn.create_stack(stack_name, template_body_str, template_parameters)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'stack_status': cfn_response.stack_status,
                'stack_status_reason': cfn_response.stack_status_reason,
                'creation_time': cfn_response.creation_time.strftime("%m/%d/%Y, %H:%M:%S")
            })
        }

    except Exception as e:
        logger.error(e)

        return {
            'statusCode': 400,
            'body': 'View application logs for more detail.'
        }


'''
load a stored event file for local development and testing
'''
def get_lambda_event_data(event_file: str):
    event_data_path = f'./lambda/tests/resources/{event_file}'
    with open(event_data_path, 'r') as data:
        return json.load(data)


'''
main - local testing and development
'''
if __name__ == '__main__':

    try:
        # use lambda/tests json files to test different event sources
        event_data = get_lambda_event_data('s3-object-created.json')

        # execute the lambda handler directly
        resp = lambda_handler(event_data, None)

    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
