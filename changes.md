# Changes

### 0.0.5
- :trophy: instance successfully starts and launches batch-init script
- install boto3 from userdata and launch batch-init as a background process
- update yum on instance start to avoid process locking
- install python3 requests to query instance region when configuring boto client
- log batch-init to a file before configuring cloudwatch for EC2 logs

### 0.0.4
- Attach IAM Role to instance
- EC2 can pull the proper resources from S3
- Add encoded userdata to stack creation
  - make an directory for processing on the instance
  - save namespace to processing directory
  - install python3
  - download batch-init.py from S3

### 0.0.3
- :trophy: completed testing of stack deployment from lambda event.  manually added EIP to puTTY onto the instance and confirm
- restructured `/lambda` for unit test with pytest.  removed lambda-out/ and lambda/build/.  Everything happens in the lambda/ directory.
- add `/lambda/test`.  only a couple of tests for now.  in progress...
- moved data for batch into `batch-processor/`
- updated `cfn-launch.sh` to build from `src/` to `build/`
- fixed stacK name errors associated with S3 event key/prefix

### 0.0.2
- ssh securty group on created ec2 instance
- restructured `cfn_launch.py` adding `cfn.py` to hold cloudformation functions

### 0.0.1
- python script for local and lambda execution (`cfn_launch.py`)
- Dockerfile to create a build container with volume mapping
    - container builds to `lambda-out/`
- `cfn-launch.sh` script for container `ENTRYPOINT`
- batch-processor, a small batch process for the pipeline goal
- template.yml to define the cloudformation template
- python container build requirements
- tag instance from argparse param or lambda event key
- readme documentation