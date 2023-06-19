#!/bin/sh

docker pull python:3.11-alpine
docker build -t cr.h.rexzhang.com/ray1ex/ddns-clienter-base . --build-arg ENV=rex --file Dockerfile.dev.base
