#!/bin/bash

set -x

for i in {3..7}
do
    echo "===== RUNNING $i =====" >> results.txt
    pypy totogram.py $i 2>&1 >> results.txt
done
