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
    - noip
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

[Example](https://github.com/rexzhang/ddns-clienter/blob/main/docs/config.toml)

## Start

```shell
docker run -dit -p 0.0.0.0:8000:8000 \
  -v /your/config.toml:/etc/ddns-clienter.toml:ro \
  --name ddns-clienter ray1ex/ddns-clienter
```

# Screenshot

## WebUI

![WebUI](https://github.com/rexzhang/ddns-clienter/blob/main/docs/image/Firefox_Screenshot_2023-02-28T07-42-35.420Z.png)

## OpenAPI

![OpenAPI](https://github.com/rexzhang/ddns-clienter/blob/main/docs/image/Firefox_Screenshot_2023-02-28T07-43-14.434Z.png)

# History

## 0.7.0

- Broken change
    - config about [addresses.XYZ], [tasks.XYZ]
- Refactor AddressProvider:XYZ

## 0.6.0 - 20230227

- Broken change
    - config about lexicon
- Update python to 3.11
- Optimizing Dockerfile
- Fix lexicon's environment variable
- Update bootstrap to 5.3.0-alpha-1(support auto dark mode)
- Update, host ninjia's js/css file
- Update, usage httpx async mode Instead of request
- Fix noip's ip detection API

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
- 如果已经有进程在执行，跳过
- 进程超时处理
- 消息推送 webhook
