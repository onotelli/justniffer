#!/usr/bin/env python
from os import environ
import re

def replace_version(text: str, new_version: str) -> str:
    text = re.sub(r"(\([\d\w.-]+.*\.)(\w*)(\))", rf"\1{new_version}\3", text)
    text = re.sub(r"\)\s*(\w+)", rf") {new_version}", text)
    print (f'version {new_version} in changelog {text}') 
    return text 



TARGET_VERSION=environ.get('DEBIAN_VERSION') 

if not TARGET_VERSION:
    print ("No version specified")
    exit(1)
else:
    with open('debian/changelog', 'r') as f:
        lines =[]
        for idx, line in enumerate(f):
            line = line.rstrip('\n')
            if idx == 0:
                new_changelog = replace_version(line, TARGET_VERSION)
            else:
                new_changelog = line
            lines.append(new_changelog)

    with open('debian/changelog', 'w') as f:
        f.write('\n'.join(lines))

# BASE_DIR=.
# version=$(echo "AC_INIT([justniffer],[0.6.7],[info@plecno.com])" | awk -F'[][]' '{print $4}')
# escaped_version=$(sed 's/\./\\./g' <<< "$version")
# echo "escaped_version $escaped_version version $version TARGET_VERSION $TARGET_VERSION"
#sed -i "1s/(${escaped_version}\.[^)]*) [^;]*;/(${version}.${TARGET_VERSION}) ${TARGET_VERSION};/" debian/changelog
