#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

dir=$1

if [[ ! -d $dir ]]; then
    echo "$dir is not a dirhectory..."
    exit 1
fi

cd $dir

logdirs=""
for entry in $(ls); do
    if [[ -d $entry && -d $entry/summary ]]; then
        logdirs="$logdirs$entry:$entry/summary,"
    fi
done

if [[ $logdirs == "" ]]; then
    echo "No summary dirs found in subfolders of $dir."
    exit 1
fi

tensorboard --logdir=$logdirs --reload_interval 30
exit 0
