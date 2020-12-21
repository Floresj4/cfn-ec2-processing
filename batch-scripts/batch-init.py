import logging, os
import argparse
import boto3, uuid
import subprocess
import requests

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
get parameters from namespace uses the get_parameters_by_path api
to request all parameters at once.
'''
def get_parameters_from_namespace(ssm, namespace: str):

    # get parameters from /some/namespace/path
    response = ssm.get_parameters_by_path(
        Path = namespace,
        Recursive = True,
        WithDecryption = False
    )

    if not response:
        raise AwsGetParametersByPathError(f'{namespace} request failed.')

    params = []
    nmspce_to_remove = namespace + '/'
    for p in response['Parameters']:
        logger.debug('Retrieved {} parameter'.format(p['Name']))

        # remove the namespace that was added
        name_only = p['Name'].replace(nmspce_to_remove, '')
        params.append((name_only, p['Value']))  #tuple

    logger.info('Get_parameters_by_path returned {} params'.format(len(params)))
    return params

'''
create the instance properties file.  outputs locally for now
'''
def create_properties_file(params: list):
    logger.info('Creating instance properties file...')
    with open('./application.properties', 'w') as out:
        for name, namespace in params:
            out_line = f'{name}={namespace}'
            out.write(out_line + '\n')
            logger.debug(out_line)

'''
get commandline options for launching the application
from this script
'''
def get_commandline_args(params: list):
    # TODO this should be sys independent
    cmdline_args = ' '.join(['--{}={}'.format(p[0], p[1]) for p in params])
    logger.debug('Generated commandline arguments to append:')
    logger.debug(f'{cmdline_args}')
    return cmdline_args

'''
get things from other AWS services
--- only s3 at the moment ---
dump outputs to the current directory
'''
def get_resource_params(params: list):
    for param in params:
        if param[1].startswith('s3://'):
            logger.info('Collecting S3 resource {}'.format(param[1]))

'''
get the namespace provided by launch.  This value will
be in a text file at the same place as this script
'''
def get_instance_namespace():
    # the value is key=value
    with open('namespace', 'r') as namefile:
        return namefile.readline().split('=')[1]


'''
get the region the instance is deployed in.  used
in configuring the boto3 client(s)
'''
def get_instance_region():
    logger.info('Querying instance region for boto client configuration')
    resp = requests.get('http://169.254.169.254/latest/meta-data/placement/region')
    return resp.text if resp.status_code == 200 else 'us-east-1'


'''
custom exception for raising and logging
'''
class AwsGetParametersByPathError(Exception):
    pass

'''
1. pull values from sources
2. create configuration file (optional)
3. start the batch-processor
'''
if __name__ == '__main__':
    logger.info('Gathering configuration...')

    namespace = get_instance_namespace()
    logger.info(f'Initializing instance...')
    logger.info(f'Namespace: {namespace}')

    instance_region = get_instance_region()

    # initialize the client for requests
    ssm = boto3.client('ssm', config = Config(
        region = instance_region,
        retries = {
            'max_attempts': 5
        }
    ))

    # get parameters
    params = get_parameters_from_namespace(ssm, namespace)
    
    # get things from other AWS services
    get_resource_params(params)

    create_properties_file(params)
    cmdline_args = get_commandline_args(params)

    logger.info('Process completed successfully.')