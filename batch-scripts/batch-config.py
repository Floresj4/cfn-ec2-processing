import boto3
import logging, os
import argparse

from botocore.config import Config
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
Deploy configuration.  Iterate properties and upload them to
a Parameter Store path.
'''
def deploy_configuration(props: Properties, nmspce: str):
    # add prefix slash if necessary
    nmspce = nmspce if nmspce[0] == '/' else '/' + nmspce

    ssm = boto3.client('ssm', config = Config(
        retries = { 'max_attempts': 5 }
    ))

    try:

        for k in props.keys():
            # create complete path and upload
            param_path = f'{nmspce}/{k}'

            response = ssm.put_parameter(
                Name = param_path,
                Value = props[k].data,
                Type = 'String',
                Overwrite = True
            )

            version = response['Version']
            logger.debug(f'Parameter {param_path} version {version} upload complete')

    except Exception as e:
        raise e


'''
load arguments required by application
'''
def init_arguments():
    parser = argparse.ArgumentParser(description = 'Migrate Configuration')
    parser.add_argument('filepath', help = 'Properties file to upload.')
    parser.add_argument('namespace', help = 'Namespace path used in property deployment {namepsace/{prop_name}={prop_value}')
    return parser.parse_args()

'''
load from properties file to Amazon Web Services
'''
def load_properties(args):
    props = Properties()
    with open(args.filepath, 'rb') as prop_file:
        props.load(prop_file, 'utf-8')

    # log it clean
    dashes = 10*'-'
    logger.info(f'{dashes}Properties loaded successfully.{dashes}')
    for k, v in props.items():
        logger.info(f'{k} = {v}')
    logger.info(dashes*5)

    return props


'''
If the batch application uses a local configuration file, take
the contents and deploy to AWS Parameter store.  The file can
be recreated during provisioning or arguments can be assembled 
for commandline usage.
'''
if __name__ == '__main__':

    try:
        logger.info('Migrating configuration...')

        args = init_arguments()
        nmspce = args.namespace

        properties = load_properties(args)
        deploy_configuration(properties, nmspce)

        logger.info('Migration completed successfully.')

    except Exception as e:
        logger.error(f'An error occurred deploying configuration: {e}')
