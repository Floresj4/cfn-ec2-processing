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

'''
If the batch application uses a local configuration file, take
the contents and deploy to AWS Parameter store.  The file can
be recreated during provisioning or arguments can be assembled 
for commandline usage.
'''
if __name__ == '__main__':
    logger.info('Migrating configuration...')

    

    logger.info('Migration completed successfully.')