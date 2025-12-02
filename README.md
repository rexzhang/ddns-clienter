# Dynamic DNS Clienter

![GitHub](https://img.shields.io/github/license/rexzhang/ddns-clienter)
![Docker Image Version (tag latest semver)](https://img.shields.io/docker/v/ray1ex/ddns-clienter/latest)
![Pytest Workflow Status](https://github.com/rexzhang/ddns-clienter/actions/workflows/check-pytest.yaml/badge.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/ray1ex/ddns-clienter)](https://hub.docker.com/r/ray1ex/ddns-clienter)

Check and update A/AAAA record to dynamic DNS provider, WebUI, support Docker

[中文文档](https://github.com/rexzhang/ddns-clienter/tree/main/docs/zh)

## Feature

- Support multiple address provider
  - [openwrt_ubus_rpc](https://openwrt.org/docs/techref/ubus#access_to_ubus_over_http), IPv4/6, recommended for use with OpenWRT
  - [hostname](https://docs.python.org/3/library/socket.html#socket.getaddrinfo), IPv4/6, recommended for use in LAN
  - [ipify](https://www.ipify.org), IPv4/6
  - [noip](https://www.noip.com/), IPv4/6
  - [ipip](https://myip.ipip.net), IPv4
  - [cip.cc](https://www.cip.cc), IPv4
  - [net.cn](http://www.net.cn), IPv4
  - [myip.la](https://myip.la)
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

## Quick Start

### Install

```shell
docker pull ray1ex/ddns-clienter
```

### Config

[Example](https://github.com/rexzhang/ddns-clienter/blob/main/examples/ddns-clienter.toml)

### Start

```shell
docker run -dit -p 0.0.0.0:8000:8000 --restart=always \
  -v $(pwd)/ddns-clienter.toml:/etc/ddns-clienter.toml:ro \
  -v $(pwd)/data:/data \
  -e TZ=Aisa/Shanghai \
  --name ddns-clienter ray1ex/ddns-clienter
```

## Screenshot

### WebUI

![WebUI](https://github.com/rexzhang/ddns-clienter/blob/main/docs/image/Firefox_Screenshot_2023-02-28T07-42-35.420Z.png)

### OpenAPI

![OpenAPI](https://github.com/rexzhang/ddns-clienter/blob/main/docs/image/Firefox_Screenshot_2023-02-28T07-43-14.434Z.png)

## Environment Variable

| Name                | Default Value in Docker   | Default Value in CLI |
| ------------------- | ------------------------- | -------------------- |
| `CONFIG_TOML`       | `/etc/ddns-clienter.toml` | `ddns-clienter.toml` |
| `DATA_PATH`         | `/data`                   | `.`                  |
| `PBULIC_INSIDE_API` | `True`                    |                      |

## History

### 1.1.0

- refactor: integrate django-vises
- refactor: migrate check_and_update to django tasks system

### 1.0.0 - 20250817

- Update python to v3.13
- feat: new address provider: `openwrt_ubus_rpc`

### 0.9.1 - 20240503

- Fix bug(infinite load events)

### 0.9.0 - 20240427

- Update python to v3.12
- Add isort into `pyproject.toml`
- Downgrade [cip.cc]'s URL to HTTP
- Add new address provider: `myip.la`
- tiger Check/Update on the web page

### 0.8.1 - 20230720

- Add HTTP header "Cache-Control" in request
- Update "ipip" and "cip.cc"'s URL to HTTPS

### 0.8.0 - 20230619

- Broken Change
  - New config file format

### 0.7.6 - 20230414

- Add, catch more crash

### 0.7.5 - 20230323

- Update, rewrite update task logic
- Update WebUI

### 0.7.4 - 20230322

- AddressProviderNetCn(net.cn)
- Fix AddressProviderCipCc(cip.cc)

### 0.7.3 - 20230316

- Add new address provider: ipip(ipip.net), cip(cip.cc)

### 0.7.2 - 20230316

- Refactor, Splitting DDNS provider dynv6 to dynv6,dynv6.rest
- Update, `task.host` is deprecated
- Update, WebUI support auto timezone
- Add, show next time in WebUI

### 0.7.1 - 20230315

- Add more debug info
- Add, display config file load error in WebUI(WIP)
- Add, display DNS info on WebUI

### 0.7.0 - 20230304

- Broken change
  - config about [addresses.XYZ], [tasks.XYZ]
- Refactor AddressProvider:XYZ
- Refactor DDNSProvider:XYZ
- Task support enable/disable;

### 0.6.0 - 20230227

- Broken change
  - config about lexicon
- Update python to 3.11
- Optimizing Dockerfile
- Fix lexicon's environment variable
- Update bootstrap to 5.3.0-alpha-1(support auto dark mode)
- Update, host ninjia's js/css file
- Update, usage httpx async mode Instead of request
- Fix noip's ip detection API

### 0.5.4 - 20220716

- Fix lexicon.cloudflare

### 0.5.3 - 20220420

- Fix IPv6 prefix update

### 0.5.2

- Fix bug

### 0.5.0

- Rewrite
- Add many dns provider support on the lexicon

### 0.4

- Add i18n support and Chinese translate

### 0.3

- New web UI

### 0.2

- Add dynv6 REST API support

### 0.1

- First release

## Trouble Shooting

## Can't detect ipv4/6 both on provider `ipify` and `noip`

Please check your Docker container DNS server, do you reach it?

## Can't detect ipv6 on provider `ipify` and `noip`, but ipv4 is ok

Please check your docker config file `/etc/docker/daemon.json`

Also, you can use the following command inside the container to test

```shell
ping6 api6.ipify.org
wget api6.ipify.org
```

ref:

- <https://docs.docker.com/config/daemon/ipv6/>
- <https://gdevillele.github.io/engine/userguide/networking/default_network/ipv6/>

## Can't detect any ip address from provider `hostname`

Please check your Docker container DNS server, Is it your local network master dns server? you can check with:

```shell
ping your-host-name
ping6 your-host-name
ping -6 your-host-name
```

### Can't detect ipv6 from provider `hostname`

check your docker host network config

in `/etc/network/interface`, like `iface enp4s0 inet6 dhcp`

## TODO

- 移除 crontab 需求?因为这会导致需要 root 权限部署 docker
- 基于群晖 DSM 的安装手册
- 更友好的用户提示
  - 当前系统时间(使用环境变量)
  - 配置文件检查
    - provider 是否存在
    - provider name 重复
  - 主页面
    - hostname 的 hostname
  - 问题处理页面
    - 各种 ping 的结果来展示问题
    - 当前 dns/时区
  - websock 提示各种状态
    - 正在执行事务
- 日志
  - 全面整理日志信息输出
  - 任务失败后的详细日志信息
    - Update task xxx failed
  - 所有 INFO 以及以上级别的 logging 自动进日志
  - 消息推送 webhook
- 安全的任务调用
  - docker 中可以 call api
  - 可以通过 token 认证
- 进程超时处理
