import logging, os
import argparse
import boto3, uuid

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
def get_parameters_from_namespace(namespace: str):
    # initialize the client for requests
    ssm = boto3.client('ssm', config = Config(
        retries = {
            'max_attempts': 5
        }
    ))

    # get parameters from /some/namespace/path
    response = ssm.get_parameters_by_path(
        Path = namespace,
        Recursive = True,
        WithDecryption = False
    )

    if not response:
        raise AwsGetParametersByPathError(f'{namespace} request failed.')

    params = []
    for p in response['Parameters']:
        logger.debug('Retrieved {} parameter'.format(p['Name']))
        params.append((p['Name'], p['Value']))  #tuple

    logger.debug(f'returning get_parameteres_by_path response: {params}')
    return params

class AwsGetParametersByPathError(Exception):
    pass

'''
1. pull values from sources
2. create configuration file (optional)
3. start the batch-processor
'''
if __name__ == '__main__':
    logger.info('Gathering configuration...')

    # the instance should have this in the environment
    namespace = os.getenv('namespace')
    logger.info(f'Initializing instance...')
    logger.info(f'Namespace: {namespace}')

    params = get_parameters_from_namespace(namespace)
    
    logger.debug(params)
    for p in params:
        logger.debug(p)

    logger.info('Process completed successfully.')