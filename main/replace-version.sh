#!/bin/bash

TARGET_VERSION=$DEBIAN_VERSION
# exit if version not specified
if [ -z "$TARGET_VERSION" ]; then
    echo "No version specified"
    exit 1 
fi
BASE_DIR=.
version=$(echo "AC_INIT([justniffer],[0.6.7],[info@plecno.com])" | awk -F'[][]' '{print $4}')
escaped_version=$(sed 's/\./\\./g' <<< "$version")
sed -i "1s/(${escaped_version}\.[^)]*) [^;]*;/(${version}.${TARGET_VERSION}) ${TARGET_VERSION};/" debian/changelog
