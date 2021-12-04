# DDNS Clienter

# Docker

## Install

```shell
docker run -dit -p 0.0.0.0:80:80 -v /tmp:/data --name ddns-clienter ray1ex/ddns-clienter
```

## Config

in `/data/config.toml`, [Example](config.toml)

# Environment Variables

## CHECK_INTERVALS

default value: `5` minutes

## PUSH_INTERVALS

default value: `1440` minutes, one day