#!/bin/bash
JUST_VERSION=0.5.9

TMP_DIR=/tmp
JUST_DIR=justniffer
JUST_DIR_VER=$JUST_DIR-$JUST_VERSION

JUST_TMP_DIR=$TMP_DIR/$JUST_DIR

rm -Rf $JUST_TMP_DIR
cd $TMP_DIR
mkdir $JUST_DIR
cd $JUST_DIR
svn co https://justniffer.svn.sourceforge.net/svnroot/justniffer/trunk/ $JUST_DIR_VER
cd $JUST_DIR_VER
find ./ -name .svn -exec rm -Rf {} \;
find ./ -name .svn -exec rm  {} \;
dpkg-buildpackage -d

