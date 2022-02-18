# Dynamic DNS Clienter

# Feature

- Support multiple address provider
    - [hostname](https://docs.python.org/3/library/socket.html#socket.getaddrinfo), recommended for use in LAN
    - [ipify](https://www.ipify.org)
- Support multiple DNS provider
    - [dynv6](https://dynv6.com/docs/apis)
    - [lexicon](https://github.com/AnalogJ/lexicon#id2)
        - Aliyun.com
        - AWS Route53
        - Cloudflare
        - DNSPod
        - GoDaddy
        - Namecheap
        - MORE, please check lexicon's document

# Quick Start

## Install

```shell
docker pull ray1ex/ddns-clienter
```

## Config

[Example](config.toml)

## Start

```shell
docker run -dit -p 0.0.0.0:8000:8000 -v /your/config.toml:/etc/ddns-clienter.toml \
 --name ddns-clienter ray1ex/ddns-clienter
```

# Dev

# TODO

- Address 条目/信息不存在
- disable 某个 task/address