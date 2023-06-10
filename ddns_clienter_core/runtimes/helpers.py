def get_dns_servers() -> list[str]:
    dns_servers = list()
    with open("/etc/resolv.conf") as f:
        for line in f:
            if line.startswith("nameserver"):
                parts = line.split()
                if len(parts) > 1:
                    dns_servers.append(parts[1])

    return dns_servers
