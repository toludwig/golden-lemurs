#!/bin/bash
docker build -t golden-lemurs .
docker run -p 127.0.0.1:8080:8080 -p 127.0.0.1:8081:8081 golden-lemurs &
python -m webbrowser http://localhost:8080/ || xdg-open http://localhost:8080/
