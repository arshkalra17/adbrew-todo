# set base image (host OS)
FROM python:3.8

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get -y update
RUN apt-get install -y curl nano wget nginx git

# Node.js + Yarn
# Pinned to Node 14: react-scripts 4 (webpack 4) does not start on Node 17+.
# The previous Yarn apt repo pulled in Debian's Node, whose version changes with
# the base image. The official tarball exists for both amd64 and arm64.
ARG NODE_VERSION=14.21.3
RUN ARCH="$(dpkg --print-architecture | sed 's/amd64/x64/')" \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1 \
    && npm install -g yarn@1.22.22

# MongoDB is no longer installed here: the `mongo` service uses the official
# mongo image (see docker-compose.yml). The old buster packages need libssl1.1,
# which current Debian does not ship, and have no ARM64 build.

# pip ships with the official Python image. The old `easy_install pip` step
# fails because easy_install no longer exists.


ENV ENV_TYPE staging
ENV MONGO_HOST mongo
ENV MONGO_PORT 27017
##########

ENV PYTHONPATH=$PYTHONPATH:/src/

# copy the dependencies file to the working directory
COPY src/requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
