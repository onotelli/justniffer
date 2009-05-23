#!/bin/bash
 
#dpkg-buildpackage -rfakeroot

DIST=$1
CREATE=$2
if [ "$DIST" == "" ]; then
  echo "usage ./build_debian.sh <distro> [create]"
  exit
fi

VERSION=`grep VERSION include/config.h| awk '{print $3}'| tail -1| tr  --delete \"`

if [ "$CREATE" == "create" ]; then
  echo "sudo DIST=$DIST pbuilder create"
fi

echo "sudo DIST=$DIST pbuilder build ../justniffer_$VERSION.dsc "

if [ "$CREATE" == "create" ]; then
  sudo pbuilder create
fi

sudo pbuilder build ../justniffer_$VERSION.dsc 
