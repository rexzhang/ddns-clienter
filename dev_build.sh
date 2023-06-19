#!/bin/zsh

docker build -t cr.h.rexzhang.com/ray1ex/ddns-clienter . --build-arg ENV=rex --file Dockerfile.dev

read -r -s -k '?Press any key to continue, push docker image...'
docker push cr.h.rexzhang.com/ray1ex/ddns-clienter

read -r -s -k '?Press any key to continue. startup container...'

docker container stop ddns-clienter
docker container rm ddns-clienter
docker run -dit -p 0.0.0.0:8000:8000 \
  -v /Users/rex/p/ddns-clienter/config.toml:/etc/ddns-clienter.toml:ro \
  --env-file .env \
  --name ddns-clienter cr.h.rexzhang.com/ray1ex/ddns-clienter
docker image prune -f
docker container logs -f ddns-clienter
