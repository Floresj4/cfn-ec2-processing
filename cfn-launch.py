import boto3
import argparse, logging
import yaml, json

'''
load the template body used in the CFN client 
call.  The template.yaml should be tested through the
wizard to minimize errors encountered through
the client call
'''
def load_template_body(template_body_path: str):
    logger.info(f'Loading Cloudformation template from {template_body_path}')

    # load as string data because AWS !Ref syntax is not standard yaml
    with open(template_body_path, 'r') as yaml_file:
        return ''.join(yaml_file.readlines())

'''
Load yaml parameters to be substituted into the template
via the client call
'''
def load_parameters(parameters_path: str):
    logger.info(f'Loading Cloudformation parameters from {parameters_path}')
    with open(parameters_path, 'r') as yaml_file:
        return yaml.load(yaml_file, Loader = yaml.FullLoader)

# initialize a logger
FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
logging.basicConfig(format = FORMAT, level = logging.INFO)
logger = logging.getLogger('cfn-logger')

# setup arguments for the script
parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
parser.add_argument('--stack_name', help = 'The name of the stack being created')
parser.add_argument('--template_body', default = './cloudformation/template.yaml', help = 'The path to the template used in the client call')
parser.add_argument('--template_parameters', default = './cloudformation/parameters.yaml', help = 'The path to the parameters used in the client call.  The AWS CFN Wizard would prompt for these values.')
args = parser.parse_args()

#collect arguments here
stack_name = args.stack_name.capitalize()
template_body = args.template_body
template_body_str = load_template_body(template_body)
template_parameters = load_parameters(args.template_parameters)

logger.debug(f'Stringified template body\n{template_body_str}')

# initialize CFN client here
logger.info(f'Creating stack named {stack_name}...')
cfn = boto3.client('cloudformation')
# cfn.create_stack(
#     StackName = stack_name,
#     TemplateBody = template_body
# )
