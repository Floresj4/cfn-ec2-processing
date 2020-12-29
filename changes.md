# Changes

### 1.0.0
- Removed instance role creation from template.yml.  Instance Role should be managed outside the template and provided as a parameter.
 
### 0.0.6
- :trophy: Successfully tested S3 deployment to EC2 processing 
- Launch the Java Spring application for data processing
- `event-data` parameter is required to indicate file to process
- `event-data` is substituted for batch-processor input commandline argument
- Eliminate duplicate input options from commandline args
- Install JDK 8 on EC2 instance

### 0.0.5
- :trophy: Instance successfully starts and launches batch-init script
- Install boto3 from userdata and launch batch-init as a background process
- Update yum on instance start to avoid process locking
- Install python3 requests to query instance region when configuring boto client
- Log batch-init to a file before configuring cloudwatch for EC2 logs

### 0.0.4
- Attach IAM Role to instance
- Lambda event creates `event-resource` parameter
  - EC2 can pull the proper resources from S3
- Add encoded userdata to stack creation
  - Make an directory for processing on the instance
  - Save namespace to processing directory
  - Install python3
  - Download batch-init.py from S3

### 0.0.3
- :trophy: Completed testing of stack deployment from lambda event.  manually added EIP to puTTY onto the instance and confirm
- Restructured `/lambda` for unit test with pytest.  removed lambda-out/ and lambda/build/.  Everything happens in the lambda/ directory.
- Add `/lambda/test`.  only a couple of tests for now.  in progress...
- Moved data for batch into `batch-processor/`
- Updated `cfn-launch.sh` to build from `src/` to `build/`
- Fixed stack name errors associated with S3 event key/prefix

### 0.0.2
- ssh securty group on created ec2 instance
- Restructured `cfn_launch.py` adding `cfn.py` to hold cloudformation functions

### 0.0.1
- Python script for local and lambda execution (`cfn_launch.py`)
- Dockerfile to create a build container with volume mapping
    - Container builds to `lambda-out/`
- `cfn-launch.sh` script for container `ENTRYPOINT`
- batch-processor, a small batch process for the pipeline goal
- template.yml to define the cloudformation template
- Python container build requirements
- Tag instance from argparse param or lambda event key
- Readme documentation