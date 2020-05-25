#!/bin/bash

IMAGE=mshade/pyhook
SHA=sha-$(git show --oneline -s | awk '{print $1}')

# Build and test
docker build -t ${IMAGE}:${SHA} .
docker tag ${IMAGE}:${SHA} ${IMAGE}:latest

if [ ! -z "$1" ]; then
  docker tag ${IMAGE}:${SHA} ${IMAGE}:${1} .
  docker push ${IMAGE}:${1}
fi

docker push ${IMAGE}:${SHA}
docker push ${IMAGE}:latest
