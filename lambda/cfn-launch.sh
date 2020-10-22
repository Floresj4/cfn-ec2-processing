#!/bin/sh
set -e

# install all requirements and copy the python script
pip3 install -r "$1/requirements.txt" -t /usr/share/lambda-temp
cp "$1/cfn-launch.py" /usr/share/lambda-temp

# create the lamda archive to the bind mount
cd /usr/share/lambda-temp
zip -r $1/lambda-out/cfn-launch.zip .