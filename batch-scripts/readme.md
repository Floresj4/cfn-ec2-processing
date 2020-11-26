# batch-scripts


### batch-init
Initialize & start the batch processing application.  This script can be executed during the instance startup stage (via UserData) on EC2 or as the container entrypoint on ECS.  *This file must be uploaded to S3 for EC2*.

Local development should set the `namespace` environment variable to be used in the Parameter Store path.  This will come from the Lambda event trigger.

    set namespace=batchprocess


### batch-config

Deploys the configuration properties required for the batch-processor application. 