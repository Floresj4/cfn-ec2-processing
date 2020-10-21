FROM centos:7

RUN yum install -y epel-release
RUN yum install -y python36
RUN yum install -y python3-pip

ARG WORKSPACE=/usr/share/workspace
ENV workspace=${WORKSPACE}

# location to mount bind the workspace to
RUN mkdir -p ${WORKSPACE}

# where pip3 install will install to
RUN mkdir -p /usr/share/lambda-temp

# location to mount bind for the output archive
RUN mkdir -p /usr/share/lambda

WORKDIR /usr/share

ADD ./lambda/cfn-launch.sh .
RUN chmod +x cfn-launch.sh

ENTRYPOINT '/usr/share/cfn-launch.sh' $workspace