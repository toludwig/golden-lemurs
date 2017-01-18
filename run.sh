#!/bin/bash

# start python server

echo "starting server..."
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
exec python3 -m "classification.eval" &

echo "starting server with webapp"
cd /home/app/webapp
exec ng serve --prod --host 0.0.0.0 --port 8080 &

exec tensorboard --logdir=/home/app/models/

echo "Finished."
wait
