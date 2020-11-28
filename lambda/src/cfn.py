import sys, os, uuid
import yaml, boto3
import logging

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
get relevant event info
'''
def  get_event_info(event):
    s3 = event['Records'][0]['s3']
    bucket = s3['bucket']['name']
    key = s3['object']['key']

    logger.info(f'Pulled bucket ({bucket}) and key ({key}) from object event')
    return bucket, key


'''
For now, handle a maven, semantic versioned, jar.  Get the stack
name and key from the resource which causes creation.
TODO prevent root namespace. 
'''
def stack_name_from_prefix(key: str):
    stack_name = key
    stack_namespace = ''

    # only handling jars at the moment
    if stack_name.endswith('.jar'):
        last_slash = key.rfind('/')
        i = 0 if last_slash < 0 else last_slash + 1

        # get attributes for instance environment
        stack_name = key[i : -4].replace('.', '')
        stack_namespace = key[:i]

        if not stack_namespace or not stack_namespace[0] == '/':
            stack_namespace = f'/{stack_namespace}'
            logger.debug(stack_namespace[0])

    logger.info(f'Attributes from key {key}: name = {stack_name}, namespace = {stack_namespace}')
    return (stack_name, stack_namespace)

'''
load the template body used in the CFN client 
call.  The template.yaml should be tested through the
wizard to minimize errors encountered through
the client call
'''
def get_object_body(template_body_path: str):
    logger.info(f'Loading Cloudformation template from {template_body_path}')

    # load as string data because AWS !Ref syntax is not standard yaml
    with open(template_body_path, 'r') as yaml_file:
        return ''.join(yaml_file.readlines())


'''
Load yaml parameters to be substituted into the template
via the client call
'''
def get_object_as_yaml(params_path: str):
    logger.info(f'Loading Cloudformation parameters from {params_path}')

    # load the string body as yaml
    yaml_body = get_object_body(params_path)
    return yaml.load(yaml_body, Loader = yaml.FullLoader)


'''
Get the body of an object stored in S3.  Uniformly log the event.
'''
def get_s3_object_body(s3, bucket: str, prefix: str):
    logger.debug(f'Retrieving S3 object body from {bucket}/{prefix}')
    obj = s3.Object(bucket, prefix)
    return obj.get()['Body'].read().decode('utf-8')


'''
initialize a cloudformation client and make a request to
create the stack/resources
'''
def create_stack(stack_name: str, template_body: str, template_parameters: []):
    # append the stack name as the Name tag on the EC2 instance
    template_parameters.append({
        'ParameterKey': 'InstanceName',
        'ParameterValue': stack_name
    })

    logger.debug(f'Stringified template body\n{template_body}')
    logger.debug(f'Template parameters\n{template_parameters}')

    #create a client token for retries, etc.
    client_reqest_token = uuid.uuid4().hex

    # initialize CFN client here
    logger.info(f'Creating stack named {stack_name}...')
    cfn = boto3.resource('cloudformation')
    stack_response = cfn.create_stack(
        StackName = stack_name,
        TemplateBody = template_body,
        Parameters = template_parameters,
        TimeoutInMinutes = 15,
        OnFailure = 'DELETE',
        Capabilities = [
            'CAPABILITY_IAM',
            'CAPABILITY_NAMED_IAM'
        ],
        ClientRequestToken = client_reqest_token
    )

    logger.info(f'Stack creation returned the following response: {stack_response}')
    return stack_response