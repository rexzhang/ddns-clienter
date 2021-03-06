# Dynamic DNS Clienter

![GitHub](https://img.shields.io/github/license/rexzhang/ddns-clienter)
![Docker Image Version (tag latest semver)](https://img.shields.io/docker/v/ray1ex/ddns-clienter/latest)
![Pytest Workflow Status](https://github.com/rexzhang/ddns-clienter/actions/workflows/check-pytest.yaml/badge.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/ray1ex/ddns-clienter)](https://hub.docker.com/r/ray1ex/ddns-clienter)

Check and update A/AAAA record to dynamic DNS provider, WebUI, support Docker

[Github](https://github.com/rexzhang/ddns-clienter)

# Feature

- Support multiple address provider
    - [hostname](https://docs.python.org/3/library/socket.html#socket.getaddrinfo), recommended for use in LAN
    - [ipify](https://www.ipify.org)
- Support multiple DNS provider
    - [dynv6](https://dynv6.com/docs/apis)
    - [lexicon](https://dns-lexicon.readthedocs.io/en/latest/configuration_reference.html)
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
docker run -dit -p 0.0.0.0:8000:8000 \
  -v /your/config.toml:/etc/ddns-clienter.toml \
  --name ddns-clienter ray1ex/ddns-clienter
```

# History

## 0.6.0 -

- Redesign config about lexicon

## 0.5.4 - 20220716

- Fix lexicon.cloudflare

## 0.5.3 - 20220420

- Fix IPv6 prefix update

## 0.5.2

- Fix bug

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
