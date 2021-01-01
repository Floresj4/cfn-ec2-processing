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
def get_client(name: str, region: str = 'us-east-1'):
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

    # event-data must exist in the param store
    # as the file to download and process
    if not 'event-data' in params.keys():
        raise Exception(f'event-data parameter is missing in namespace {namespace}')

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
get objects from S3
'''
def download_s3_resources(s3, params: dict):
    for k,v in params.items():
        if v.startswith('s3://'):

            try:
                logger.info(f'Collecting S3 resource {v} from {k} param')
                
                # get s3 attributes from resource path
                bucket, key, filename = get_download_attributes(v)

                # download the current directory of execution
                logger.debug(f'Downloading S3 object: {bucket}, {key}, {filename}')
                s3.download_file(bucket, key, f'./{filename}')

            except Exception as e:
                logger.error('An error occurred downloading {}: {}'.format(v, str(e)))


'''
get commandline options for launching the application
from this script
'''
def get_commandline_args(params: dict):
    cmdline_args = []
    
    # exclude event-resource and change event-data
    for k,v in params.items():

        # ignore the jar and the input param to replace
        if k in ['event-resource', 'datafile-path']:
            continue

        # change the event-data to what the batch-processor
        # would require as an input file
        if k == 'event-data':
            attrs = get_download_attributes(v)
            cmdline_args.append('--datafile-path=./{}'.format(attrs[2]))
        else:
            cmdline_args.append(f'--{k}={v}')

    cmdline_args = ' '.join(cmdline_args)
    logger.info('Generated commandline arguments to append:')
    logger.info(f'{cmdline_args}')
    return cmdline_args


'''
get download attributes from an s3 resource path
'''
def get_download_attributes(s3_path: str):
    path = s3_path.replace('s3://', '')
    bucket_sep = path.find('/')
    file_sep = path.rfind('/')
    bucket = path[:bucket_sep]
    key = path[bucket_sep + 1:]
    filename = path[file_sep + 1:]
    return (bucket, key, filename)


'''
get the namespace provided by launch.  This value will
be in a text file at the same place as this script
'''
def get_instance_namespace():
    # the value is key=value
    with open('namespace', 'r') as namefile:
        return namefile.readline().rstrip('\n').split('=')[1]


'''
get the from and to email addresses.  From email 'noreply@...'
will exist in a global space of param store.  The To email will
be provided along with the processing namespace
'''
def get_mail_params(namespace: str):
    pass


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
    # execute the process and ensure a zero return code
    subprocess_exc = ['java', '-jar', app_name, cmdline_args]

    logger.info(f'** Launching {app_name}...')
    logger.info('** Executing {}'.format(' '.join(subprocess_exc)))
    process = subprocess.run(subprocess_exc)
    process.check_returncode()


'''
get the application name from the event-resource.  it is created
when the lambda function is triggered.
'''
def name_from_event_resource(params: dict):
    if not 'event-resource' in params.keys():
        raise Exception('The event-resource key is required for processing.')

    last_delim = params['event-resource'].rfind('/')
    return params['event-resource'][last_delim + 1:]


'''

'''
class BatchInitMailer(object):

    def __init__(self, namespace: str):
        self.namespace = namespace

        # get the default no-reply email
        self.src_email = self.__get_param_value('no-reply-email')
        self.dest_email = self.__get_param_value(f'{namespace}/email')
        
        # enable mailing if both parameters were populated
        self.mail_enabled = self.src_email and self.dest_email

    '''
    Get a parameter value or return None
    '''
    def __get_param_value(self, param_name: str):
        logger.info(f'Querying SSM parameter {param_name}')

        ssm = get_client('ssm')
        response = ssm.get_parameter(
            Name = param_name,
            WithDecryption = False
        )

        logger.debug(f'Query response: {response}')
        return response['Value'] if response else None


    '''
    Send an email the signal the start of processing
    '''
    # def send_start_email(src_email: str, dest_email: list):

    #     ses = get_client('ses', region)
    #     response = ses.send_email(
    #         Source = self.src_email,
    #         Destination = {
    #             'ToAddresses': dest_email
    #         },
    #         Message = {
    #             'Subject': {
    #                 'Data': 'Batch Processing Start',
    #                 'Charset': 'utf-8'
    #             },
    #             'Body': {
    #                 'Text': {
    #                     'Data': 'Hello, world.',
    #                 },
    #                 'Html': {
    #                     'Data': '<h3>Hello, world.</h3>'
    #                 }
    #             }
    #         }
    #     )

    #     logger.info(f'SendMail response {response}')


    def send_finish_email():
        pass

'''
custom exception for raising and logging
'''
class AwsGetParametersByPathError(Exception):
    pass


'''
1. pull ssm parameter
2. pull s3 object resources
3. create commandline argument string
4. create configuration file
5. start the batch-processor
'''
if __name__ == '__main__':
    try:
        logger.info('Gathering configuration...')

        namespace = get_instance_namespace()
        logger.info(f'Namespace: {namespace}')

        # initialize the client for requests
        region = get_instance_region()
        ssm = get_client('ssm', region)
        s3 = get_client('s3', region)

        from_address, to_address = get_mail_params(namespace)

        # # get parameters
        # params = get_parameters_from_namespace(ssm, namespace)
        # app_name = name_from_event_resource(params)

        # # save s3 objects to the current directory
        # download_s3_resources(s3, params)

        # # create a properties file and cmd args from params
        # create_properties_file(params)
        # cmdline_args = get_commandline_args(params)

        # launch_process(app_name, cmdline_args)

        logger.info('Process completed successfully.')
    
    except Exception as e:
        logger.error(f'Processing encountered an error: {e}')
