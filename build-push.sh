#!/bin/bash

docker build -t mshade/pyhook:latest .

if [ ! -z "$1" ]; then
  docker build -t mshade/pyhook:${1} .
  docker push mshade/pyhook:${1}
fi

docker push mshade/pyhook:latest

