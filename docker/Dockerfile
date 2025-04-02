FROM ubuntu:24.04

RUN apt-get update -y && \
    apt-get install -y libboost-python-dev \
        libboost-regex-dev libboost-program-options-dev libboost-iostreams-dev \
        libboost-thread-dev libpcap0.8-dev python3-dev python-is-python3 g++ gcc make \
        dpkg-dev debhelper

CMD [ "tail", "-f", "/dev/null" ]