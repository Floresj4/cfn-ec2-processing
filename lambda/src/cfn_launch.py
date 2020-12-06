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
        stack_name, stack_namespace = cfn.stack_name_from_prefix(key)

        cfn.put_event_resource_param(stack_namespace, bucket, key)

        # get template body from S3
        s3 = boto3.resource('s3')
        template_body_str = cfn.get_s3_object_body(s3, 'floresj4-cloudformation', 'template.yml')

        # add the stack namespace to the instance environment
        # template_body_str

        # get template params for S3
        params_str = cfn.get_s3_object_body(s3, 'floresj4-cloudformation', 'params.yml')
        template_parameters = yaml.load(params_str, Loader = yaml.FullLoader)

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
main - local testing and development
'''
if __name__ == '__main__':

    # setup arguments for the script
    parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
    parser.add_argument('stack_name', help = 'The name of the stack being created')
    parser.add_argument('--template_body', default = './cloudformation/template.yml', help = 'The path to the template used in the client call')
    parser.add_argument('--template_parameters', default = './cloudformation/params.yml', help = 'The path to the parameters used in the client call.  The AWS CFN Wizard would prompt for these values.')
    args = parser.parse_args()

    try:
        #collect arguments here
        stack_name = args.stack_name.capitalize()

        # pull local resources here
        templ_body = cfn.get_object_body(args.template_body)
        templ_params = cfn.get_object_as_yaml(args.template_parameters)
        
        # execute the client request to create
        resp = cfn.create_stack(stack_name, templ_body, templ_params)
        logger.debug({
            'stack_status': resp.stack_status,
            'stack_status_reason': resp.stack_status_reason,
            'creation_time': resp.creation_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
