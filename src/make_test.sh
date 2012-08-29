#!/bin/bash

g++ test.cpp -I /usr/include/python2.7 -l boost_python -l python2.7 -o test -I ../lib/libnids-1.21_patched/src/
