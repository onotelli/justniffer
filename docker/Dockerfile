ARG BASE_IMAGE=ubuntu:24.04
ARG PYTHON_VERSION

FROM ${BASE_IMAGE} AS dev_env
ARG PYTHON_VERSION
ENV PYTHON_VERSION=${PYTHON_VERSION}
RUN apt-get update -y && \
    apt-get install -y libboost-python-dev \
        libboost-regex-dev libboost-program-options-dev libboost-iostreams-dev \
        libboost-thread-dev libpcap0.8-dev python3-dev python-is-python3 g++ gcc make \
        dpkg-dev debhelper
    

FROM dev_env AS build_env
COPY / /workspace
RUN cd /workspace && dpkg-buildpackage -d

FROM ${BASE_IMAGE}
COPY --from=build_env /*.deb /
RUN apt-get update -y && \
for deb in /*.deb ; do apt-get install -y ./"$deb"; done && \
rm  /*.deb



CMD [ "tail", "-f", "/dev/null" ]
