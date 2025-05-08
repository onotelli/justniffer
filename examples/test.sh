#!/bin/bash
# sudo justniffer  -e ./test.sh -l dest.ip:%dest.ip:%dest.port%newline%request  -i any  

while read inputline
do 
    text=`echo "$inputline" | grep -i -E  host\|dest\.ip`
    if [ "$text" != "" ]; then
        echo $text;
    fi;
done