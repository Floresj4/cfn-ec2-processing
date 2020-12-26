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
    logging.basicConfig(format = FORMAT, filename = 'batch-init.log')
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))
    return logger

logger = initialize_logger()
clients = {}

'''
create a boto client instance.
'''
def get_client(name: str, region: str):
    if not name in clients:
        clients[name] = boto3.client(name, config = Config(
            region_name = region,
            retries = { 'max_attempts': 5 }
        ))

    return clients[name]

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
        # remove the namespace that was added
        name_only = p['Name'].replace(nmspce_to_remove, '')
        logger.debug('Retrieved {} parameter'.format(name_only))
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
    cmdline_args = ' '.join(['--{}={}'.format(p[0], p[1]) for p in params])
    logger.debug('Generated commandline arguments to append:')
    logger.debug(f'{cmdline_args}')
    return cmdline_args

'''
get objects from S3
'''
def get_s3_resources(s3, params: list):
    for param in params:
        if param[1].startswith('s3://'):
            logger.info('Collecting S3 resource {}'.format(param[1]))

            # with open()
            # s3.download_fileobj()

'''
get the namespace provided by launch.  This value will
be in a text file at the same place as this script
'''
def get_instance_namespace():
    # the value is key=value
    with open('namespace', 'r') as namefile:
        return namefile.readline().rstrip('\n').split('=')[1]


'''
get the region the instance is deployed in.  used
in configuring the boto3 client(s)
'''
def get_instance_region():
    try:
        logger.info('Querying instance region for boto client configuration')
        resp = requests.get('http://169.254.169.254/latest/meta-data/placement/region')
        return resp.text if resp.status_code == 200 else 'us-east-1'
    except Exception:
        logger.error('Unable to query instance metadata for region.  Default us-east-1')
        return 'us-east-1'


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
    logger.info(f'Namespace: {namespace}')

    # initialize the client for requests
    region = get_instance_region()
    ssm = get_client('ssm', region)
    s3 = get_client('s3', region)

    # get parameters
    params = get_parameters_from_namespace(ssm, namespace)

    get_s3_resources(s3, params)

    # create a properties file and cmd args
    create_properties_file(params)
    cmdline_args = get_commandline_args(params)

    logger.info('Process completed successfully.')