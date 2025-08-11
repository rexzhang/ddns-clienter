# Dynamic DNS Client(DDNS-Clienter) 中文文档

## 安装并启动容器

```shell
docker run -dit -p 0.0.0.0:8000:8000 --restart=always \
  -v $(pwd)/ddns-clienter.toml:/etc/ddns-clienter.toml:ro \
  -v $(pwd)/data:/data \
  -e TZ=Aisa/Shanghai \
  --name ddns-clienter ray1ex/ddns-clienter
```

- `$(pwd)/ddns-clienter.toml` 为配置文件
  - 文件格式请参考 `examples/ddns-clienter.toml`
  - 范例文件中有更详细的配置说明

## 获取 IP 地址

### 通过 `openwrt_ubus_rpc`

- [通过 OpenWRT 的 ubus RPC 协议](https://openwrt.org/docs/techref/ubus#access_to_ubus_over_http)来获取与识别
- 适合于网络环境中使用了 OpenWRT 路由器
- 当前只实现了获取 wan/wan_6 接口的 IPv4/6 地址

### 通过 `hostname`

- 通过计算机系统的 `hostname` 来获取与识别
- 使用 [Python 的 getaddrinfo 方法](https://docs.python.org/3/library/socket.html#socket.getaddrinfo)
- 适用于获取局域网内部的 IP 地址, 比如内网设备的公网 IPv6 地址

### 通过地址检测服务商

- 各家的的具体协议大同小异,基本上都是基于 HTTP 协议的 GET 方法
- 大部分供应商都只能(或比较好的)支持 IPv4
- 如果你的路由器上有特别的路由策略,可能需要针对服务商的域名作相应设置;以解决解析出错误地址的问题
- 获取到的地址取决与发起请求的服务器与提供服务器之间的所有网络节点行为
- 适合用来获取 IPv4 真.公网地址

#### 当前支持的地址检测服务商清单

| 名称     | IP  | 服务商域名                |
| -------- | --- | ------------------------- |
| `ipify`  | 4/6 | `ipify.org`               |
| `noip`   | 4/6 | `ip1.dynupdate.no-ip.com` |
| `ipip`   | 4   | `myip.ipip.net`           |
| `cip.cc` | 4   | `www.cip.cc`              |
| `net.cn` | 4   | `www.net.cn`              |

### 检测规则

- 每整 5 分钟执行一次检测

## 更新 A/AAAA 记录到 DNS 服务商

### 支持的 DNS 服务商

#### [dynv6](https://dynv6.com/docs/apis)

- dynv6 是一家不错的很早就支持 IPv6 的动态域名解析服务商
- 免费, 但是平均一年会出现一次服务不可用的问题

#### [lexicon](https://dns-lexicon.readthedocs.io/en/latest/configuration_reference.html)

- 一个支持几乎所有主流商业域名解析服务商的软件包
- 本项目通过整合这个软件包来支持大部分的服务商(如:阿里云/DNSPod/Cloudflare...)

### 更新规则

- 相应的配置条目发生了变化
- 当检测到相应的 IP 地址发生变化时
- IP 地址没有变化,但是上次更新到现在已经超过强制更新周期时间
  - 强制更新周期为 1440 分钟

## 常见问答集

### 使用 `hostname` 获取不到地址,或者获取错误

- 可以使用类似 `ping -6 ds920` 命令来查看主机名为 `ds920` 的 IPv6 地址

### 通过地址检测服务商获取到的地址不是本地网络的公网地址

- 在主路由处查看公网的 IPv4 地址,以进行核对
- 路由器中是否有特别的路由策略(比如双出口导致获取到的公网地址不是自己想设定的那个)

### 查看/修改时区

- 时区不正确会导致网页上显示的时间不对
- 系统默认的时区为 UTC, 即格林威治时间
- 在 Trouble Shooting(救生圈) 页面会列出当前系统时区
- 设置容器环境变量 `TZ` 为 `Asia/Shanghai` 可以将系统时区改为东 8 区

### 查看/修改系统 DNS 服务器地址

- 小概率情况下,如果 DNS 设置为非局域网主路由器提供的 DNS, IP 地址获取失败或错误
- 在 Trouble Shooting(救生圈) 页面会列出当前系统使用的 DNS
- 修改有两个方法
  - 容器启动的命令行中添加 `--dns 192.168.1.1` 参数
  - 创建一个 `resolv.conf` 文件, 映射到容器中的 `/etc/resolv.conf`
    - 文件内容为 `nameserver 192.168.1.1`
    - 其中 `192.168.1.1` 为你想重新指定的 DNS 服务器地址
