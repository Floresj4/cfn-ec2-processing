# batch-scripts


### batch-init
Initialize & start the batch processing application.  This script can be executed during the instance startup stage (via UserData) on EC2 or as the container entrypoint on ECS.  *This file must be uploaded to S3 for EC2*.

### batch-config

Deploys configuration properties required for the batch-processor application. 

From the root directory

    py .\batch-scripts\batch-config.py {filepath} {namespace}

 will deploy configuration from filepath into AWS with the {namespace} prefix.  Use `batch-config.py --h` for more information.