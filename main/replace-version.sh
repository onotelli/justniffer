#!/bin/bash

TARGET_VERSION=$DEBIAN_VERSION
# exit if version not specified
if [ -z "$TARGET_VERSION" ]; then
    echo "No version specified"
    exit 1 
fi
cd /workspace
version=$(/workspace/src/justniffer --version | awk 'NR==1{print $2}')
escaped_version=$(sed 's/\./\\./g' <<< "$version")
sed -i "1s/(${escaped_version}\.[^)]*) [^;]*;/(${version}.${TARGET_VERSION}) ${TARGET_VERSION};/" debian/changelog
