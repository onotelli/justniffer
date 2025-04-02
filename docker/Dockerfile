FROM ubuntu:22.04 AS dev_env

RUN apt-get update -y && \
    apt-get install -y libboost-python-dev \
        libboost-regex-dev libboost-program-options-dev libboost-iostreams-dev \
        libboost-thread-dev libpcap0.8-dev python3-dev python-is-python3 g++ gcc make \
        dpkg-dev debhelper
    

FROM dev_env AS build_env
COPY / /workspace
RUN cd /workspace && dpkg-buildpackage -d

FROM ubuntu:22.04
COPY --from=build_env /*.deb /
RUN apt-get update -y && apt install -y ./justniffer_0.5.21.noble_amd64.deb


CMD [ "tail", "-f", "/dev/null" ]
