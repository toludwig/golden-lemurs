#!/bin/bash
#docker build -t golden-lemurs .
docker run -a stdout -a stdin -w "/home/app/" golden-lemurs "./classify.sh" "<$1" ">$2"
