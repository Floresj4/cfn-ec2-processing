import sys, os, uuid
import yaml, base64
import logging

import boto3
from botocore.config import Config

'''
initialize logger
'''
def initialize_logger(name: str = __name__):
    FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
    logging.basicConfig(format = FORMAT)
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))
    return logger

logger = initialize_logger()


'''
check for the existence of parameters at a particular
namespace.  fail if none are present
'''
def check_namespace_parameters(namespace: str):
    logger.info(f'Checking existence of event-data in {namespace} parameters')

    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameters_by_path(
            Path = namespace,
            Recursive = False,
            WithDecryption = False
        )

        # event-data needs to exist, at least
        for param in response['Parameters']:
            if param['Name'].endswith('event-data'):
                logger.info('{} parameter found.'.format(param['Name']))
                return
        
        # fail if event-data wasn't set
        raise Exception(f'{namespace} exists, but event-data was not found.')

    except Exception as e:
        logger.error(f'Unable to verify namespace parameter (event-data): {e}')
        raise e


'''
get relevant event info
'''
def get_event_info(event):
    s3 = event['Records'][0]['s3']
    bucket = s3['bucket']['name']
    key = s3['object']['key']

    logger.info(f'Pulled bucket ({bucket}) and key ({key}) from object event')
    return bucket, key


'''
Add event resource to param store as well.
Instance init will read this to know which resource to run
'''
def put_event_resource_param(namespace: str, bucket: str, key: str):
    ssm = boto3.client('ssm', config = Config(
        retries = { 'max_attempts': 5 }
    ))

    #add a separator and create the parameter name
    sep = '/' if not namespace[-1:] == '/' else ''
    param_path = f'{namespace}{sep}event-resource'
    param_value = f's3://{bucket}/{key}'

    logger.info(f'Putting event-resource parameter: {param_path}')
    response = ssm.put_parameter(
        Name = param_path,
        Value = param_value,
        Type = 'String',
        Overwrite = True
    )
    
    if not response:
        raise Exception(f'Putting {param_path} failed.')

    return response


'''
For now, handle a maven, semantic versioned, jar.  Get the stack
name and key from the resource which causes creation.
'''
def get_attributes_from_key(key: str):
    stack_name = key
    stack_namespace = ''

    # only handling jars at the moment
    if stack_name.endswith('.jar'):
        last_slash = key.rfind('/')
        i = 0 if last_slash < 0 else last_slash + 1

        # get attributes for instance environment
        stack_name = key[i : -4].replace('.', '')
        stack_namespace = key[:i]

        # TODO do not use the jar name for root uploads anymore
        if not stack_namespace or stack_namespace == '/':
            stack_namespace = f'/{stack_name}'
        elif not stack_namespace[0] == '/':
            stack_namespace = f'/{stack_namespace}'

    logger.info(f'Attributes from key {key}: name = {stack_name}, namespace = {stack_namespace}')
    return (stack_name, stack_namespace)

'''
load the template body used in the CFN client 
call.  The template.yaml should be tested through the
wizard to minimize errors encountered through
the client call
'''
def get_object_body(template_body_path: str):
    logger.info(f'Loading Cloudformation template from {template_body_path}')

    # load as string data because AWS !Ref syntax is not standard yaml
    with open(template_body_path, 'r') as yaml_file:
        return ''.join(yaml_file.readlines())


'''
Load yaml parameters to be substituted into the template
via the client call
'''
def get_object_as_yaml(params_path: str):
    logger.info(f'Loading Cloudformation parameters from {params_path}')

    # load the string body as yaml
    yaml_body = get_object_body(params_path)
    return yaml.load(yaml_body, Loader = yaml.FullLoader)


'''
Get the body of an object stored in S3.  Uniformly log the event.
'''
def get_s3_object_body(s3, bucket: str, prefix: str):
    logger.debug(f'Retrieving S3 object body from {bucket}/{prefix}')
    obj = s3.Object(bucket, prefix)
    return obj.get()['Body'].read().decode('utf-8')

'''
get ec2-userdata to add into the cloudformation create request
'''
def get_user_data(bucket_path, name, namespace):
    batch_dir = '/batch-processing'

    userdata = ['#!/bin/sh',
        f'yum update -y',
        f'mkdir -p {batch_dir} && cd {batch_dir} && touch {batch_dir}/namespace',
        f'echo namespace={namespace} >> {batch_dir}/namespace',
        f'aws s3 cp s3://{bucket_path}/batch-init.py {batch_dir}',
        f'yum install -y java-1.8.0',
        f'yum install -y python3',
        f'python3 -m pip install boto3',
        f'python3 -m pip install requests',
        f'python3 batch-init.py &'
    ]

    stringified = '\n'.join(userdata)
    logger.info(f'Generating instance UserData: {stringified}')
    encoded_userdata = base64.b64encode(stringified.encode('utf-8'))
    return str(encoded_userdata, 'utf-8')

'''
initialize a cloudformation client and make a request to
create the stack/resources
'''
def create_stack(stack_name: str, template_body: str, template_parameters: []):
    logger.debug(f'Stringified template body\n{template_body}')
    logger.debug(f'Template parameters\n{template_parameters}')

    #create a client token for retries, etc.
    client_reqest_token = uuid.uuid4().hex

    # initialize CFN client here
    logger.info(f'Creating stack named {stack_name}...')
    cfn = boto3.resource('cloudformation')
    stack_response = cfn.create_stack(
        StackName = stack_name,
        TemplateBody = template_body,
        Parameters = template_parameters,
        TimeoutInMinutes = 15,
        OnFailure = 'DELETE',
        Capabilities = [
            'CAPABILITY_IAM',
            'CAPABILITY_NAMED_IAM'
        ],
        ClientRequestToken = client_reqest_token
    )

    logger.info(f'Stack creation returned the following response: {stack_response}')
    return stack_response