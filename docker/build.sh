#!/bin/bash

docker build  -f Dockerfile.debian .. -t debian-justniffer
docker run -it --rm -v $(pwd):/mnt debian-justniffer /bin/bash -c "cp /workspace/*.deb /mnt/ && ls -l /mnt/" 

