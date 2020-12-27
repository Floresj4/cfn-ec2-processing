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
    logging.basicConfig(format = FORMAT, filename = 'batch-init.log', filemode = 'w')
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

    params = {}
    nmspce_to_remove = namespace + '/'
    for p in response['Parameters']:
        # remove the namespace that was added
        name_only = p['Name'].replace(nmspce_to_remove, '')
        logger.debug('Retrieved {} parameter'.format(name_only))
        params[name_only] = p['Value']

    logger.info('Get_parameters_by_path returned {} params'.format(len(params)))
    return params

'''
create the instance properties file.  outputs locally for now
'''
def create_properties_file(params: dict):
    logger.info('Creating instance properties file...')
    with open('./application.properties', 'w') as out:
        for key, value in params.items():
            out_line = f'{key}={value}'
            out.write(out_line + '\n')
            logger.debug(out_line)

'''
get commandline options for launching the application
from this script
'''
def get_commandline_args(params: dict):
    cmdline_args = ' '.join([f'--{k}={v}' for k,v in params.items()])
    logger.info('Generated commandline arguments to append:')
    logger.info(f'{cmdline_args}')
    return cmdline_args

'''
get objects from S3
'''
def get_s3_resources(s3, params: dict):
    for k,v in params.items():
        if v.startswith('s3://'):

            try:
                logger.info(f'Collecting S3 resource {v} from {k} param')
                
                # get s3 attributes from parameter
                path = v.replace('s3://', '')
                bucket_sep = path.find('/')
                file_sep = path.rfind('/')
                bucket = path[:bucket_sep]
                key = path[bucket_sep + 1:]
                filename = path[file_sep + 1:]

                # download the current directory of execution
                logger.debug(f'Downloading S3 object: {bucket}, {key}, {filename}')
                s3.download_file(bucket, key, f'./{filename}')

            except Exception as e:
                logger.error('An error occurred downloading {}: {}'.format(v, str(e)))


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
launch the java application to process data
'''
def launch_process(app_name: str, cmdline_args: str):
    logger.info('Launching batch processor...')

    # execute the process and ensure a zero return code
    process = subprocess.run(['java', '-jar', app_name, cmdline_args])
    process.check_returncode()


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

    # save s3 objects to the current directory
    get_s3_resources(s3, params)

    # create a properties file and cmd args from params
    create_properties_file(params)
    cmdline_args = get_commandline_args(params)

    # launch_process(cmdline_args)

    logger.info('Process completed successfully.')