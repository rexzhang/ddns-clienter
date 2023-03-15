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

## 0.7.0 - 20220304

- Broken change
    - config about [addresses.XYZ], [tasks.XYZ]
- Refactor AddressProvider:XYZ
- Refactor DDNSProvider:XYZ
- Task support enable/disable;

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

# Trouble Shooting

## Can't detect ipv4/6 both on provider `ipify` and `noip`

check your Docker container DNS server, do you reach it ?

## Can't detect any ip address from provider `hostname`

check your Docker container DNS server, is it your local network master dns server? you can check with:

```shell
ping your-host-name
ping6 your-host-name
ping -6 your-host-name
```

## Can't detect ipv6 from provider `hostname`

check your docker host network config

in `/etc/network/interface`, like `iface enp4s0 inet6 dhcp`

# TODO

- 用户错误提示友好
    - 在 WebUI 提示配置错误
    - 显示任务正在执行
- 日志
    - 全面整理日志信息输出
    - 所有 INFO 以及以上级别的logging自动进日志
    - 消息推送 webhook
- 安全的任务调用
    - docker中可以call api
    - 可以通过 token 认证
- 进程超时处理
