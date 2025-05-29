#!/usr/bin/env python
from os import environ
import re

def replace_version(text: str, new_version: str) -> str:
#text = "justniffer (0.6.8-dev.2.jammy) jammy; urgency=low"

    # Replace the last part of the version string inside the parentheses
    text = re.sub(r"\(([\d\w.-]+)\.(\w+)\)", rf"(\1.{new_version})", text)
    # Replace the word after the parentheses
    text = re.sub(r"\)\s*(\w+)", rf") {new_version}", text)
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
