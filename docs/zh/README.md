# 安装并启动容器

```shell
docker pull ray1ex/ddns-clienter
docker run -dit -p 0.0.0.0:8000:8000 --restart=always \
  -v /your/config.toml:/etc/ddns-clienter.toml:ro \
  --name ddns-clienter ray1ex/ddns-clienter
```

- `/your/config.toml` 为配置文件, 文件格式已经内容见...

# IP 地址获取

## 获取地址的方法

### 通过 `hostname`

- 通过计算机系统的 `hostname` 来获取与识别
- 使用 [Python 的 getaddrinfo 方法](https://docs.python.org/3/library/socket.html#socket.getaddrinfo)
- 适用于局域网内部
- 对获取 IPv6 地址优势比较大

### 通过地址检测服务商

- 各家的的具体协议大同小异,基本上都是基于 HTTP 协议的 GET 方法
- 大部分供应商都只能(或比较好的)支持 IPv4
- 如果你的路由器上有特别的路由策略,可能需要针对服务商的域名作相应设置;以解决解析出错误地址的问题
- 获取到的地址取决与发起请求的服务器与提供服务器之间的所有网络节点行为
- 对获取 IPv4 公网地址优势比较大

#### 当前支持的地址检测服务商清单

| 名称       | IP  | 服务商域名                     |
|----------|-----|---------------------------|
| `ipify`  | 4/6 | `ipify.org`               |
| `noip`   | 4/6 | `ip1.dynupdate.no-ip.com` |
| `ipip`   | 4   | `myip.ipip.net`           |
| `cip.cc` | 4   | `www.cip.cc`              |
| `net.cn` | 4   | `www.net.cn`              |

## 检测规则

- 每整 5 分钟执行一次检测

# DDNS A/AAAA 记录更新

## 支持的 DNS 服务商

### [dynv6](https://dynv6.com/docs/apis)

- dynv6 是一家不错的很早就支持 IPv6 的动态域名解析服务商
- 免费, 但是平均一年会出现一次服务不可用的问题

### [lexicon](https://dns-lexicon.readthedocs.io/en/latest/configuration_reference.html)

- 一个支持几乎所有主流商业域名解析服务商的软件包
- 本项目通过整合这个软件包来支持大部分的服务商(如:阿里云/DNSPod/Cloudflare...)

## 更新规则

- 当检测到相应的 IP 地址发生变化时
- IP 地址没有变化,但是上次更新到现在已经超过强制更新周期时间
    - 强制更新周期为 1440 分钟

# 常见问答集

## 使用 `hostname` 获取不到地址,或者获取错误

- 可以使用类似 `ping -6 ds920` 命令来查看主机名为 `ds920` 的 IPv6 地址

## 通过地址检测服务商获取到的地址不是本地网络的公网地址

- 在主路由处查看公网的IPv4地址,以进行核对
- 路由器中是否有特别的路由策略(比如双出口导致获取到的公网地址不是自己想设定的那个)

## 查看/修改时区

- 时区不正确会导致网页上显示的时间不对
- 系统默认的时区为 UTC, 即格林威治时间
- 在每个 Web 页面的左下角处, 均会显示当前系统时区
- 设置容器环境变量 `TZ` 为 `Asia/Shanghai` 可以将系统时区改为东8区

## 查看/修改系统 DNS 服务器地址

- 小概率情况下,如果 DNS 设置为非局域网主路由器提供的 DNS, IP 地址获取失败或错误
- 在每个 Web 页面的左下角处, 均会显示当前系统使用的 DNS
- 修改有两个方法
    - 容器启动的命令行中添加 `--dns 192.168.1.1` 参数
    - 创建一个 `resolv.conf` 文件, 映射到容器中的 `/etc/resolv.conf`
        - 文件内容为 `nameserver 192.168.1.1`
        - 其中 `192.168.1.1` 为你想重新指定的 DNS 服务器地址