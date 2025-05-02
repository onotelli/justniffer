#!/bin/bash

while IFS= read -r line
do
    echo -e "$line" | cat -v
done

echo "-----------------------------------------------------"
