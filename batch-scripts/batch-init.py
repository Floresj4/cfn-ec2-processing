import boto3
import logging, os

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

def get_client(name: str):
    pass

def get_parameter_namespace(namespace: str):
    return f'/com/flores/{namespace}'

'''
1. pull values from Parameter Store based on environment info
'''
if __name__ == '__main__':
    logger.info('Gathering configuration...')

    env_namespace = os.getenv('namespace')
    param_path = get_parameter_namespace(env_namespace)
    logger.debug(f'Parameter path: {param_path}')

    logger.info('Process completed successfully.')