---
name: python-get-ip
description: Get host IP address using Python. Use this skill when you need to retrieve the local IPv4/IPv6 address, all network interface addresses, or the public IP address of the current machine.
---

# Python 获取主机 IP 地址

**使用 Python 获取主机 IP 地址** — 涵盖本地 IP、所有网卡地址、公网 IP 等多种场景。

## When to Use This Skill

**触发条件（自动应用）:**

- 需要获取主机本地 IP 地址
- 需要枚举所有网络接口及其地址
- 需要获取公网（外网）IP 地址
- 需要区分 IPv4 与 IPv6 地址
- 需要跨平台兼容的网络信息查询

## Quick Reference

### 方法一：使用 `socket`（标准库，最常用）

```python
import socket

def get_local_ip() -> str:
    """获取本机对外使用的 IPv4 地址（无需网络连接）"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # 连接一个公网地址（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

print(get_local_ip())  # 例如：192.168.1.100
```

### 方法二：获取主机名对应的 IP

```python
import socket

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"主机名: {hostname}")
print(f"IP 地址: {ip}")
```

> ⚠️ 该方法在某些系统上可能返回 `127.0.0.1`，推荐使用方法一。

### 方法三：使用 `psutil` 获取所有网卡信息

```python
import psutil
import socket

def get_all_interfaces():
    """获取所有网络接口的 IP 地址"""
    interfaces = {}
    for name, addrs in psutil.net_if_addrs().items():
        ips = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ips.append({"ipv4": addr.address, "netmask": addr.netmask})
            elif addr.family == socket.AF_INET6:
                ips.append({"ipv6": addr.address})
        if ips:
            interfaces[name] = ips
    return interfaces

for iface, addrs in get_all_interfaces().items():
    print(f"{iface}: {addrs}")
```

**安装依赖：**

```bash
pip install psutil
```

### 方法四：使用 `netifaces` 获取网卡详情

```python
import netifaces

def get_all_ips():
    """获取所有网卡的 IPv4 地址"""
    result = {}
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            result[iface] = addrs[netifaces.AF_INET][0]["addr"]
    return result

print(get_all_ips())
# 示例输出：{'lo': '127.0.0.1', 'eth0': '192.168.1.100'}
```

**安装依赖：**

```bash
pip install netifaces
```

### 方法五：获取公网 IP

```python
import urllib.request
import json

def get_public_ip() -> str:
    """获取公网 IP（需要互联网连接）"""
    url = "https://api.ipify.org?format=json"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read())["ip"]

print(get_public_ip())  # 例如：203.0.113.42
```

**使用 `requests` 库（更简洁）：**

```python
import requests

def get_public_ip() -> str:
    return requests.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
```

## 常见场景

### 场景 1：服务启动时打印监听地址

```python
import socket

ip = get_local_ip()
port = 8080
print(f"服务启动，监听地址：http://{ip}:{port}")
```

### 场景 2：判断是否在局域网

```python
import ipaddress

def is_private_ip(ip: str) -> bool:
    return ipaddress.ip_address(ip).is_private

print(is_private_ip("192.168.1.1"))   # True
print(is_private_ip("203.0.113.42"))  # False
```

### 场景 3：过滤回环地址

```python
import socket
import psutil

def get_non_loopback_ips():
    """获取所有非回环 IPv4 地址"""
    ips = []
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ips.append(addr.address)
    return ips

print(get_non_loopback_ips())
```

### 场景 4：同时获取 IPv4 和 IPv6

```python
import socket

def get_ip_both(host: str = "dns.google") -> dict:
    """同时解析 IPv4 和 IPv6"""
    results = {"ipv4": [], "ipv6": []}
    for info in socket.getaddrinfo(host, None):
        family, _, _, _, sockaddr = info
        if family == socket.AF_INET:
            results["ipv4"].append(sockaddr[0])
        elif family == socket.AF_INET6:
            results["ipv6"].append(sockaddr[0])
    return results
```

## 方法对比

| 方法 | 依赖 | 适用场景 | 可靠性 |
| :--- | :--- | :--- | :--- |
| `socket` + UDP trick | 标准库 | 获取对外 IP | ⭐⭐⭐⭐⭐ |
| `socket.gethostbyname` | 标准库 | 简单场景 | ⭐⭐⭐ |
| `psutil` | 第三方 | 枚举所有网卡 | ⭐⭐⭐⭐⭐ |
| `netifaces` | 第三方 | 跨平台网卡详情 | ⭐⭐⭐⭐ |
| HTTP API | 网络请求 | 获取公网 IP | ⭐⭐⭐（需联网） |

## 完整工具函数

```python
import socket
import ipaddress
from typing import Optional

def get_local_ip() -> str:
    """获取本机对外 IPv4 地址"""
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
    import urllib.request
    import json
    try:
        url = "https://api.ipify.org?format=json"
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())["ip"]
    except Exception:
        return None

if __name__ == "__main__":
    local = get_local_ip()
    print(f"主机名:   {get_hostname()}")
    print(f"本地 IP:  {local}")
    print(f"是私网:   {is_private(local)}")
    print(f"公网 IP:  {get_public_ip()}")
```

## 故障排除

### 问题 1：返回 `127.0.0.1`

使用 `socket.gethostbyname(hostname)` 时可能发生。

**修复：** 改用 UDP trick 方法（方法一）。

### 问题 2：多网卡时返回错误接口的 IP

**修复：** 使用 `psutil` 枚举所有接口，按需过滤（如过滤 `lo`、`docker0`）。

### 问题 3：IPv6 地址包含区域 ID（`%eth0`）

```python
ip = "fe80::1%eth0"
clean_ip = ip.split("%")[0]  # fe80::1
```

### 问题 4：公网 IP 获取超时

**修复：** 设置合理超时，或使用备用 API：

```python
FALLBACK_APIS = [
    "https://api.ipify.org?format=json",
    "https://api4.my-ip.io/ip.json",
    "https://ipinfo.io/json",
]
```

## 参考资源

- **标准库文档**: <https://docs.python.org/3/library/socket.html>
- **psutil 文档**: <https://psutil.readthedocs.io/>
- **netifaces PyPI**: <https://pypi.org/project/netifaces/>
- **ipify API**: <https://www.ipify.org/>
- **脚本示例**: `scripts/get_ip.py`
