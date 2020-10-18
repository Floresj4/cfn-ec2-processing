import boto3
import argparse, logging
import yaml, json

'''
load the template body used in the CFN client 
call.  The template.yaml should be tested through the
wizard to minimize errors encountered through
the client call
'''
def load_template_body(path: str):
    logger.info(f'Loading cloudformation template from {path}')
    with open(path, 'r') as yaml_file:
        return ''.join(yaml_file.readlines())

# initialize a logger
FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
logging.basicConfig(format = FORMAT, level = logging.INFO)
logger = logging.getLogger('cfn-logger')

# setup arguments for the script
parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
parser.add_argument('--stack_name', help = 'The name of the stack being created')
parser.add_argument('--template_body', default = './template.yaml', help = 'The template URI used in stack creation')
args = parser.parse_args()

#collect arguments here
stack_name = args.stack_name.capitalize()
template_body = args.template_body
template_body_str = load_template_body(template_body)

logger.debug(f'Stringified template body\n{template_body_str}')

# initialize CFN client here
logger.info(f'Creating stack named {stack_name}...')
cfn = boto3.client('cloudformation')
# cfn.create_stack(
#     StackName = stack_name,
#     TemplateBody = template_body
# )
