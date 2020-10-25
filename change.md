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

### 0.0.2

- ssh securty group on created ec2 instance
- restructured `cfn_launch.py` adding `cfn.py` to hold cloudformation functions