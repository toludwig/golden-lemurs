#!/bin/bash

logdirs=""
for entry in $(ls); do
    if [[ -d $entry ]]; then
        logdirs="$logdirs$entry:$entry/summary,"
    fi
done

tensorboard --logdir=$logdirs
