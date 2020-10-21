#!/bin/sh
set -e

# install all requirements and copy the python script
pip3 install -r "$1/requirements.txt" -t /usr/share/lambda-temp
cp "$1/cfn-launch.py" /usr/share/lambda-tempcp

# create the lamda archive to the bind mount
zip -r /usr/share/workspace/lambda/cfn-launch.zip /usr/share/workspace/lambda