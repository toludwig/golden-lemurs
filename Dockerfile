# Tensorflow Dockerfile

FROM ubuntu:14.04

MAINTAINER Fabian Richter <fabianrichter97@gmail.com>

# general stuff
RUN apt-get update
RUN apt-get install -y build-essential
# Python
RUN apt-get install -y --no-install-recommends python3-pip python3 python3-dev python3-numpy python3-scipy curl gzip unzip

# Nodejs
RUN curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -

RUN apt-get install -y --no-install-recommends nodejs


COPY classification /home/app/classification/
COPY data /home/app/data/
COPY webapp /home/app/webapp/
COPY docs /home/app/docs/
COPY models /home/app/models/
COPY scripts /home/app/scripts/

# Word2Vec
#COPY "word2vec/GoogleNews-vectors-negative300.bin.gz" "/home/app/data/GoogleNews-vectors-negative300.bin.gz"
WORKDIR /home/app/data/
RUN ["gunzip", "GoogleNews-vectors-negative300.bin.gz"]
RUN ["unzip", "data.zip"]
RUN ["unzip", "dev.zip"]
RUN ["unzip", "docs.zip"]
RUN ["unzip", "edu.zip"]
RUN ["unzip", "extensions.zip"]
RUN ["unzip", "homework.zip"]
RUN ["unzip", "web.zip"]

WORKDIR /home/app/webapp
RUN ["npm", "install"]
RUN ["npm", "install", "-g", "angular-cli"]

WORKDIR /home/app
COPY setup.py "/home/app/"
RUN ["pip3", "install", "-e", "."]
RUN ["pip3", "install", "--upgrade", "https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.12.1-cp34-cp34m-linux_x86_64.whl"]

EXPOSE 8080 8080
EXPOSE 8081 8081
EXPOSE 6006 6006

COPY run.sh "/home/app/"

CMD "./run.sh"
