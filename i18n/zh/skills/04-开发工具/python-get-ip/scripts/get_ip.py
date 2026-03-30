#!/usr/bin/env python3
"""
get_ip.py - 获取主机 IP 地址工具脚本

用法:
    python get_ip.py          # 显示本地 IP 和公网 IP
    python get_ip.py --all    # 显示所有网卡信息
"""

import argparse
import ipaddress
import json
import socket
import urllib.request
from typing import Optional


def get_local_ip() -> str:
    """获取本机对外 IPv4 地址（UDP trick，无需实际网络连接）"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_hostname() -> str:
    """获取主机名"""
    return socket.gethostname()


def is_private(ip: str) -> bool:
    """判断是否为私网地址"""
    return ipaddress.ip_address(ip).is_private


def get_public_ip(timeout: int = 5) -> Optional[str]:
    """获取公网 IP，失败返回 None"""
    apis = [
        "https://api.ipify.org?format=json",
        "https://ipinfo.io/json",
    ]
    for url in apis:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                data = json.loads(resp.read())
                return data.get("ip")
        except Exception:
            continue
    return None


def get_all_interfaces() -> dict:
    """获取所有网络接口的 IP 地址（需要 psutil）"""
    try:
        import psutil  # type: ignore

        interfaces = {}
        for name, addrs in psutil.net_if_addrs().items():
            ips = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ips.append({"type": "IPv4", "address": addr.address, "netmask": addr.netmask})
                elif addr.family == socket.AF_INET6:
                    ips.append({"type": "IPv6", "address": addr.address.split("%")[0]})
            if ips:
                interfaces[name] = ips
        return interfaces
    except ImportError:
        print("⚠️  请安装 psutil：pip install psutil")
        return {}


def main():
    parser = argparse.ArgumentParser(description="获取主机 IP 地址")
    parser.add_argument("--all", action="store_true", help="显示所有网卡信息")
    parser.add_argument("--public", action="store_true", help="仅显示公网 IP")
    args = parser.parse_args()

    if args.public:
        ip = get_public_ip()
        print(ip if ip else "无法获取公网 IP")
        return

    local = get_local_ip()
    print(f"主机名:   {get_hostname()}")
    print(f"本地 IP:  {local}")
    print(f"是私网:   {is_private(local)}")

    if args.all:
        print("\n所有网卡：")
        for iface, addrs in get_all_interfaces().items():
            for addr in addrs:
                addr_str = addr["address"]
                if addr["type"] == "IPv4":
                    addr_str += f"/{addr.get('netmask', '')}"
                print(f"  {iface:15s} [{addr['type']}] {addr_str}")
    else:
        pub = get_public_ip()
        print(f"公网 IP:  {pub or '获取失败（检查网络连接）'}")


if __name__ == "__main__":
    main()
