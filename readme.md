# Data Processing w/ Cloudformation and EC2

An exploratory project to launch an EC2 instance and begin a batch processing job based on some trigger event.

Objectives
 - A new release of the batch component will trigger processing via upload to S3
 - AWS Lambda will launch and configure an EC2 instance
 - Options to the processing event can be externalized and easily mananged between events

Change information can be found [here](./changes.md).

## Folders
[batch-scripts](./batch-scripts/) - scripts for configuring and launching

[batch-processor/](./batch-processor/) - the java project to perform processing on the EC2 instance

[cloudformation/](./cloudformation/) - contains cloudformation templates

[lambda/](./lambda/) - the lambda function initiating the stack creation event.

## Dockerfile

Dockerfile is used to create the lambda deployment archive.  AWS Lambda runs on Linux and there are some scenarios where a deployment created on a Windows machine will not run on Linux &ndash; pyopenssl and cryptography to name a few.

The docker build command will create and tag a container.  This command is intended to be run from the project root.

`docker build -t cfn-launch-lambda .`

The `cfn-launch-lambda container` is intended to bind mount the root directory and output the .zip deployment to lambda/build/.  Bind mount allows the archive to be recreated without rebuilding the container image.

The `-v` option binds the current directory to `/usr/share/workspace` on the container.  The container ENTRYPOINT will install and package requirements for the deployment archive.

The command below will run the build container to produce the archive.

`docker run -v "%CD%":/usr/share/workspace cfn-launch-lambda:latest`

Upload lambda function code to S3.

`aws s3 cp .\lambda\build\cfn-launch.zip s3://...`

Update lambda to the latest execution

`aws lambda update-function-code --function-name ... --s3-bucket ... --s3-key cfn-launch.zip --publish`
