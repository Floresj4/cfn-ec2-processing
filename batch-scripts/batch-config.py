import boto3
import logging, os
import argparse

from jproperties import Properties

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
load from properties file to Amazon Web Services
'''
def load_properties(args):
    props = Properties()
    with open(args.filepath, 'rb') as prop_file:
        props.load(prop_file, 'utf-8')

    dashes = 10*'-'
    logger.info(f'{dashes}Properties loaded successfully.{dashes}')
    for k, v in props.items():
        logger.info(f'{k} = {v}')

    logger.info(dashes * 2)
    return props

'''
If the batch application uses a local configuration file, take
the contents and deploy to AWS Parameter store.  The file can
be recreated during provisioning or arguments can be assembled 
for commandline usage.
'''
if __name__ == '__main__':
    logger.info('Migrating configuration...')

    parser = argparse.ArgumentParser(description = 'Migrate Configuration')
    parser.add_argument('filepath', help = 'Properties file to upload.')
    args = parser.parse_args()

    try:

        properties = load_properties(args)

        logger.info('Migration completed successfully.')

    except Exception as e:
        print(e)
        logger.error(str(e))
