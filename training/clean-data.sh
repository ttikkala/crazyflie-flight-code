#!/bin/bash
for foldername in *; do
    echo "$foldername"
    for filename in ./$foldername/*; do
        echo "$filename"
        [ -e "$filename" ] || continue
        python3 clean-training-data.py "$filename"
    done
done

