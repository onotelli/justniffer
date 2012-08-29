#!/bin/bash

g++ test.cpp utilities.cpp -I /usr/include/python2.7 -l boost_python -l python2.7 -l pcap -o test -I ../lib/libnids-1.21_patched/src/
