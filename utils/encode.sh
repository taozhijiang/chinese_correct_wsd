#!/bin/bash

for file in `ls *.txt`; do
    echo "Processing:"$file
    enca -L zh_CN -x UTF-8 < $file > $file".dat"
done
