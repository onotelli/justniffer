#!/bin/bash

TARGET_VERSION=$DEBIAN_VERSION
cd /workspace/justniffer
version=$(/workspace/justniffer/src/justniffer --version | awk 'NR==1{print $2}')
escaped_version=$(sed 's/\./\\./g' <<< "$version")
sed -i "1s/(${escaped_version}\.[^)]*) [^;]*;/(${version}.${TARGET_VERSION}) ${TARGET_VERSION};/" debian/changelog
