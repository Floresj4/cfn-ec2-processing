#!/bin/sh
set -e

# install all requirements and copy the python script
pip3 install -r "$1/lambda/requirements.txt" -t /usr/share/lambda-temp
cp $1/lambda/src/*.py /usr/share/lambda-temp/

# create the lamda archive to the bind mount
cd /usr/share/lambda-temp
zip -r $1/lambda/build/cfn-launch.zip .