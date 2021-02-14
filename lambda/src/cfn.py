import sys, os, uuid
import yaml, base64
import logging

import boto3
from botocore.config import Config

'''
initialize logger
'''
def initialize_logger(name: str = __name__):
    logging.basicConfig(format = '[%(levelname)s]:%(asctime)s %(message)s')
    lggr = logging.getLogger(name)
    lggr.setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))
    return lggr

logger = initialize_logger()
clients = {}


'''
create a boto client instance.
'''
def get_client(name: str, region: str = 'us-east-1', proxies: dict = None):
    if not name in clients:
        clients[name] = boto3.client(name, config = Config(
            proxies = proxies,
            region_name = region,
            retries = { 'max_attempts': 5 }
        ))

    return clients[name]


class CFN(object):

    def __init__(self, cfn_bucket: str, cfn_key: str):
        self.cfn_bucket = cfn_bucket
        self.cfn_key = cfn_key


    '''
    check for the existence of parameters at a particular
    namespace.  fail if none are present
    '''
    def verify_namespace(self, namespace: str):
        logger.info('Checking existence of event-data in %s parameters', namespace)

        try:
            ssm = get_client('ssm')
            response = ssm.get_parameters_by_path(
                Path = namespace,
                Recursive = False,
                WithDecryption = False
            )

            # event-data needs to exist, at least
            for param in response['Parameters']:
                if param['Name'].endswith('event-data'):
                    logger.info('%s parameter found.', param['Name'])
                    return True
            
            return False

        except Exception as e:
            logger.error('Unable to verify namespace parameter (event-data): %s', e)
            raise e


    '''
    get relevant event info
    '''
    def get_event_info(self, event):
        s3 = event['Records'][0]['s3']
        bucket = s3['bucket']['name']
        key = s3['object']['key']

        logger.info(f'Pulled bucket ({bucket}) and key ({key}) from object event')
        return bucket, key


    '''
    Add event resource to param store as well.
    Instance init will read this to know which resource to run
    '''
    def put_event_resource_param(self, namespace: str, bucket: str, key: str):
        #add a separator and create the parameter name
        sep = '/' if not namespace[-1:] == '/' else ''
        param_path = f'{namespace}{sep}event-resource'
        param_value = f's3://{bucket}/{key}'

        logger.info('Putting event-resource parameter: %s', param_path)

        ssm = get_client('ssm')
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
    return the name of the cloudformation stack.  Uses
    the event object name after dropping the suffix
    '''
    def get_name(self, key: str):
        last_slash = key.rfind('/')
        
        i = 0 if last_slash < 0 else last_slash + 1
        stack_name = key[i : -4].replace('.', '')
        return stack_name


    '''
    return the namespace used in parameter store.  combine the strings, remove
    the artifact name, and correct for parameter store conventions /ab/c/def
    '''
    def get_namespace(self, bucket: str, key: str):
        last_sep = key.rfind('/')
        rm_name = '' if last_sep == -1 else key[:last_sep]
        return f'/{bucket}/{rm_name}/'.replace('//', '/')


    '''
    load the template body used in the CFN client 
    call.  The template.yaml should be tested through the
    wizard to minimize errors encountered through
    the client call
    '''
    def get_object_body(self, template_body_path: str):
        logger.info(f'Loading Cloudformation template from {template_body_path}')

        # load as string data because AWS !Ref syntax is not standard yaml
        with open(template_body_path, 'r') as yaml_file:
            return ''.join(yaml_file.readlines())


    '''
    Load yaml parameters to be substituted into the template
    via the client call
    '''
    def get_object_as_yaml(self, params_path: str):
        logger.info('Loading Cloudformation parameters from %s', params_path)

        # load the string body as yaml
        yaml_body = self.get_object_body(params_path)
        return yaml.load(yaml_body, Loader = yaml.FullLoader)


    '''
    load the template body as a string because it has non-standard (AWS) yaml
    macros: !Ref, etc.
    '''
    def get_template_body_as_string(self):
        s3 = get_client('s3')
        return self.__get_s3_object_body(s3, self.cfn_bucket, self.cfn_key)


    '''
    return parameters to inject into the template in a yaml format
    '''
    def get_template_params_as_yaml(self):
        s3 = get_client('s3')
        params_str = self.__get_s3_object_body(s3, self.cfn_bucket, 'params.yml')
        return yaml.load(params_str, Loader = yaml.FullLoader)


    '''
    Get the body of an object stored in S3.  Uniformly log the event.
    '''
    def __get_s3_object_body(self, s3, bucket: str, key: str):
        logger.debug('Retrieving S3 object body from %s/%s', bucket, key)
        obj = s3.get_object(Bucket = bucket, Key = key)
        return obj['Body'].read().decode('utf-8')


    '''
    get ec2-userdata to add into the cloudformation create request
    '''
    def get_user_data(self, namespace):
        batch_dir = '/batch-processing'
        bucket_path = self.cfn_bucket

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
        logger.info('Generating instance UserData: %s', stringified)
        encoded_userdata = base64.b64encode(stringified.encode('utf-8'))
        return str(encoded_userdata, 'utf-8')


    '''
    initialize a cloudformation client and make a request to
    create the stack/resources
    '''
    def create_stack(self, stack_name: str, template_body: str, template_parameters: []):
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