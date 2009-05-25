#!/bin/bash
 
#dpkg-buildpackage -rfakeroot

DIST=$1
CREATE=$2
PYTHON=$3

if [ "$DIST" == "--help" ]; then
  echo "usage ./build_debian.sh <distro> [create|nocreate] [python|nopython] "
  exit
fi

VERSION=`grep VERSION include/config.h| awk '{print $3}'| tail -1| tr  --delete \"`

if test "$DIST" == ""; then
  DIST=`cat /etc/lsb-release| grep DISTRIB_CODENAME| awk  -F= '{print $2}'`
  echo "distro codename not specified: assumed $DIST"
fi

if [ "$CREATE" == "create" ]; then
  echo "sudo DIST=$DIST pbuilder create"
fi

if [ "$python" == "python" ]; then
  cp debian/control.python debian/control
esle
  cp debian/control.nopython debian/control
fi

dpkg-buildpackage

echo "sudo DIST=$DIST pbuilder build ../justniffer_$VERSION.dsc "

if [ "$CREATE" == "create" ]; then
  sudo DIST=$DIST pbuilder create
fi

sudo DIST=$DIST pbuilder build ../justniffer_$VERSION.dsc 
