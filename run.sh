#!/bin/bash

# start python server

echo "todo: starting python server with trained network"

echo "starting server with webapp"
cd /home/app/webapp
exec ng serve --host 0.0.0.0 --port 4200

echo "Finished."

while true; end;
