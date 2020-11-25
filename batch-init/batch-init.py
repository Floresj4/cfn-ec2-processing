import boto3
import logging, os

'''
initialize logger
'''
def initialize_logger(name: str = __name__):
    FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
    logging.basicConfig(format = FORMAT)
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))
    return logger

logger = initialize_logger()

'''
1. pull values from Parameter Store based on environment info
'''
if __name__ == '__main__':
    logger.info('Gathering configuration...')
    logger.info('Process completed successfully.')