# Tensorflow Dockerfile

FROM ubuntu:14.04

MAINTAINER Fabian Richter <fabianrichter97@gmail.com>

# general stuff
RUN apt-get update
RUN apt-get install -y build-essential
# Python
RUN apt-get install -y --no-install-recommends python3-pip python3 python3-dev python3-numpy python3-scipy curl gzip

# Nodejs
RUN curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -

RUN apt-get install -y --no-install-recommends nodejs

# Word2Vec

#git lfs
RUN build_deps="curl ca-certificates" && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${build_deps} && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git-lfs && \
    git lfs install && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -r /var/lib/apt/lists/*

# download
RUN ["mkdir", "/home/app"]
WORKDIR /home/app
RUN ["git", "clone", "https://github.com/mmihaltz/word2vec-GoogleNews-vectors.git", "word2vec"]

COPY classification /home/app/classification/
COPY data /home/app/data/
RUN ["gunzip", "-c", "word2vec/GoogleNews-vectors-negative300.bin.gz", ">data/GoogleNews-vectors-negative300.bin"]
# COPY docs /home/app/docs/ # symlink in web app
COPY models /home/app/models
COPY webapp /home/app/webapp/

WORKDIR /home/app/webapp
RUN ["npm", "install"]
RUN ["npm", "install", "-g", "angular-cli"]

WORKDIR /home/app
COPY requirements.txt "/home/app/"
RUN ["pip3", "install", "-e", "."]
# RUN ["pip3", "install", "--upgrade", "https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0-cp34-cp34m-linux_x86_64.whl"]


EXPOSE 4200 4200

COPY run.sh "/home/app/"

CMD "./run.sh"
