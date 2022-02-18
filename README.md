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

# History

## 0.5.0

- Rewrite
- Add many dns provider support on the lexicon

## 0.4

- Add i18n support and Chinese translate

## 0.3

- New web UI

## 0.2

- Add dynv6 REST API support

## 0.1

- First release

# TODO

- Address 条目/信息不存在
- disable 某个 task/address