import boto3, sys, os
import argparse, logging
import yaml, json
import uuid

'''
initialize logger
'''
def initialize_logger():
    FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
    logging.basicConfig(format = FORMAT)
    logger = logging.getLogger(__name__)
    logger.setLevel(os.getenv('LOGGING_LEVEL', 'INFO'))
    return logger

logger = initialize_logger()

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
def load_parameters(params_path: str):
    logger.info(f'Loading Cloudformation parameters from {params_path}')
    with open(params_path, 'r') as yaml_file:
        return yaml.load(yaml_file, Loader = yaml.FullLoader)

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
        ClientRequestToken = client_reqest_token
    )

    logger.info(f'Stack creation returned the following response: {stack_response}')
    return stack_response

'''
Get the body of an object stored in S3.  Uniformly log the event.
'''
def get_s3_object_body(s3, bucket: str, prefix: str):
    logger.debug(f'Retrieving S3 object body from {bucket}/{prefix}')
    obj = s3.Object(bucket, prefix)
    return obj.get()['Body'].read().decode('utf-8')

'''
lambda entrypoint
'''
def lambda_handler(event, context):

    # there could be multiple records
    s3 = event['Records'][0]['s3']
    bucket = s3['bucket']['name']
    key = s3['object']['key']

    # stackname will be the object creating the event
    idx = key.rfind('/')
    idx = 0 if idx <= 0 else idx + 1
    stack_name = key[idx:]

    # get template body from S3
    s3 = boto3.resource('s3')
    template_body_str = get_s3_object_body(s3, 'floresj4-cloudformation', 'template.yml')

    # get template params for S3
    params_str = get_s3_object_body(s3, 'floresj4-cloudformation', 'params.yml')
    template_parameters = yaml.load(params_str, Loader = yaml.FullLoader)

    # execute the client request to create
    stack_response = create_stack(stack_name, template_body_str, template_parameters)

    return {
        'statusCode': 200,
        'body': json.dumps(stack_response)
    }

'''
main - local testing and development
'''
if __name__ == '__main__':

    # setup arguments for the script
    parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
    parser.add_argument('stack_name', help = 'The name of the stack being created')
    parser.add_argument('--template_body', default = './cloudformation/template.yml', help = 'The path to the template used in the client call')
    parser.add_argument('--template_parameters', default = './cloudformation/params.yml', help = 'The path to the parameters used in the client call.  The AWS CFN Wizard would prompt for these values.')
    args = parser.parse_args()

    try:
        #collect arguments here
        stack_name = args.stack_name.capitalize()

        templ_body = get_object_body(args.template_body)

        templ_params = get_object_body(args.template_parameters)
        templ_params = yaml.load(templ_params, Loader = yaml.FullLoader)
        
        # execute the client request to create
        stack_response = create_stack(stack_name, templ_body, templ_params)

    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
