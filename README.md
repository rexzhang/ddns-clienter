# Dynamic DNS Clienter

# Address Provider

## hostname

Recommended for use in LAN

## ipify

https://www.ipify.org/

# Dynamic DNS Provider

## dynv6

https://dynv6.com/docs/apis
Update API and REST API mix

# Docker

## Install

```shell
docker run -dit -p 0.0.0.0:80:80 -v /tmp:/data --name ddns-clienter ray1ex/ddns-clienter
```

## Config

in `/data/config.toml`, [Example](config.toml)

## Environment Variables

### CHECK_INTERVALS

default value: `5` minutes

### FORCE_UPDATE_INTERVALS

default value: `1440` minutes, one day

### SENTRY_DSN

default value: None

# Dev

# TODO

- Address 条目/信息不存在
- disable 某个 task/address