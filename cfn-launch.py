import boto3
import argparse, logging

# initialize a logger
FORMAT = '[%(levelname)s]:%(asctime)s %(message)s'
logging.basicConfig(format = FORMAT, level = logging.INFO)
logger = logging.getLogger('cfn-logger')

# setup arguments for the script
parser = argparse.ArgumentParser(description = 'Cloudformation launch script')
parser.add_argument('--stack_name', help = 'The name of the stack being created')
args = parser.parse_args()

#collect arguments here
stack_name = args.stack_name

# begin stack creation
logger.info(f'Creating stack {stack_name}')

# initialize CFN client here
cfn = boto3.client('cloudformation')
