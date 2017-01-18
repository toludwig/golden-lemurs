#!/bin/bash
docker build -t golden-lemurs .
docker run -p 127.0.0.1:4200:4200 golden-lemurs &
python -m webbrowser http://localhost:4200/ || xdg-open http://localhost:4200/
