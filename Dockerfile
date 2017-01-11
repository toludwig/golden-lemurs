# Tensorflow Dockerfile

FROM ubuntu:14.04

MAINTAINER Fabian Richter <fabianrichter97@gmail.com>

# general stuff
RUN apt-get update
RUN apt-get install -y build-essential
# Python
RUN apt-get install -y --no-install-recommends python3-pip python3 python3-dev python3-numpy python3-scipy curl

# Nodejs
RUN curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -

RUN apt-get install -y --no-install-recommends nodejs

RUN ["mkdir", "/home/app"]
COPY ["classification", "data", "docs", "webapp", "/home/app/"]

WORKDIR /home/app/webapp
RUN ["npm", "install"]
RUN ["npm", "install", "-g", "angular-cli"]

WORKDIR /home/app
COPY requirements.txt "/home/app/"
RUN ["pip3", "install", "-r", "requirements.txt"]
RUN ["pip3", "install", "--upgrade", "https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0-cp34-cp34m-linux_x86_64.whl"]


EXPOSE 4200 4200

COPY run.sh "/home/app/"

CMD "./run.sh"
