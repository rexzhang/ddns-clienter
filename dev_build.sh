#!/bin/sh

docker container stop ddns-clienter
docker container rm ddns-clienter
docker image rm cr.rexzhang.com:55555/ray1ex/ddns-clienter

docker build -t cr.rexzhang.com:55555/ray1ex/ddns-clienter . --build-arg ENV=rex --file Dockerfile.dev
#docker push cr.rexzhang.com:55555/ray1ex/ddns-clienter

docker run -dit -p 0.0.0.0:8000:8000 \
  -v /Users/rex/p/ddns-clienter/config.toml:/etc/ddns-clienter.toml:ro \
  --env-file .env \
  --name ddns-clienter cr.rexzhang.com:55555/ray1ex/ddns-clienter
docker image prune -f
docker container logs -f ddns-clienter
