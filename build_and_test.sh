#!/bin/sh

docker container stop ddns-clienter
docker container rm ddns-clienter
docker image rm ray1ex/ddns-clienter

docker pull python:3.11-alpine
docker build -t ray1ex/ddns-clienter . --build-arg ENV=rex

docker run -dit -p 0.0.0.0:8000:8000 \
  -v /Users/rex/p/ddns-clienter/config.toml:/etc/ddns-clienter.toml:ro \
  --env-file .env \
  --name ddns-clienter ray1ex/ddns-clienter
docker image prune -f
docker container logs -f ddns-clienter
