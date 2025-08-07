import httpx
from pprint import pprint

router_ip = "192.168.200.1"
username = "root"
password = "84129270"


def get_wan_ip_ubus():
    try:
        ubus_url = f"http://{router_ip}/ubus"
        session_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [
                "00000000000000000000000000000000",
                "session",
                "login",
                {"username": username, "password": password},
            ],
        }

        client = httpx.Client()

        # 获取会话token
        session_response = client.post(ubus_url, json=session_payload)
        # pprint(session_response.json())
        if session_response.status_code != 200:
            return None

        session_data = session_response.json()
        pprint(session_data)
        ubus_rpc_session = session_data["result"][1]["ubus_rpc_session"]

        # 获取网络信息
        network_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "call",
            # "params": [ubus_rpc_session, "network.interface.wan", "status", {}],
            "params": [ubus_rpc_session, "network.interface.wan", "dump", {}],
            # "params": [ubus_rpc_session, "network.device", "status", {}],
            # "params": [ubus_rpc_session, "file", "read", {"path": "/etc/board.json"}],
        }

        network_response = client.post(ubus_url, json=network_payload)
        if network_response.status_code == 200:
            network_data = network_response.json()
            pprint(network_data)
            ipv4 = network_data["result"][1].get("ipv4-address", [])
            if ipv4:
                return ipv4[0]["address"]

    except Exception as e:
        print(f"UBUS Error: {str(e)}")

    return None


get_wan_ip_ubus()
