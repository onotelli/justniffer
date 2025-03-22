FROM ubuntu:24.04

RUN apt-get update -y && \
    apt-get install -y curl bind9-dnsutils iputils-ping netcat-openbsd iproute2 software-properties-common

RUN add-apt-repository -y ppa:oreste-notelli/ppa && \
    apt-get update -y && \
    apt-get install -y justniffer

CMD [ "tail", "-f", "/dev/null" ]