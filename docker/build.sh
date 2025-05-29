#!/bin/bash


DEBIAN_VERSIONS=("trixie" "bookworm")
for version in "${DEBIAN_VERSIONS[@]}"
do
    echo "Building Docker image for Debian $version..."
    docker build --build-arg DEBIAN_VERSION=$version -f Dockerfile.debian .. -t debian-justniffer-$version
    echo "Running container for Debian $version..."
    docker run -it --rm -v $(pwd):/mnt debian-justniffer-$version /bin/bash -c "cp /workspace/*.deb /mnt/ && ls -l /mnt/"    
    echo "Finished processing Debian $version!"
done


