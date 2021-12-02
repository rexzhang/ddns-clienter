docker container stop ddns-clienter
docker container rm ddns-clienter
docker image rm ddns-clienter

docker pull python:3.10-alpine
docker build -t ray1ex/ddns-clienter .
# shellcheck disable=SC2046
docker rmi -f $(docker images -qa -f "dangling=true")

docker run -dit -p 0.0.0.0:8000:80 -v /tmp:/data --name ddns-clienter ray1ex/ddns-clienter