import sys, os
import argparse, logging
import yaml, json
import uuid

import boto3
from botocore.config import Config

import cfn

logger = cfn.initialize_logger()


'''
lambda entrypoint
'''
def lambda_handler(event, context):
    try:
        # there could be multiple records...
        # stackname will be the object creating the event
        bucket, key = cfn.get_event_info(event)
        stack_name, stack_namespace = cfn.get_attributes_from_key(key)
        
        # update the namespace to contain the bucket name
        stack_namespace = f'/{bucket}' + stack_namespace

        # put the event resource param for the instance to download
        cfn.put_event_resource_param(stack_namespace, bucket, key)

        # get template body from S3
        s3 = boto3.resource('s3')
        template_body_str = cfn.get_s3_object_body(s3, 'floresj4-cloudformation', 'template.yml')

        # get template params for S3
        params_str = cfn.get_s3_object_body(s3, 'floresj4-cloudformation', 'params.yml')
        template_parameters = yaml.load(params_str, Loader = yaml.FullLoader)

        # get the encoded userdata
        instance_userdata = cfn.get_user_data('floresj4-cfn-ec2-processing',
            stack_name, stack_namespace)

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

    # setup arguments for the script
    parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
    parser.add_argument('--template_body', default = './cloudformation/template.yml', help = 'The path to the template used in the client call')
    parser.add_argument('--template_parameters', default = './cloudformation/params.yml', help = 'The path to the parameters used in the client call.  The AWS CFN Wizard would prompt for these values.')
    args = parser.parse_args()

    try:
        # use lambda/tests json files to test different event sources
        event_data = get_lambda_event_data('s3-object-created.json')

        # execute the lambda handler directly
        resp = lambda_handler(event_data, None)

    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
