#!/usr/bin/env python3

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_host_socket(ip, port=80, timeout=1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0
    except:
        return False

def check_host_multiple_ports(ip, timeout=1):
    common_ports = [80, 443, 22, 23, 53, 135, 139, 445, 3389, 8080]
    
    for port in common_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))
                if result == 0:
                    return True, port
        except:
            continue
    return False, None

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname if hostname != ip else "Unknown"
    except:
        return "Unknown"

def scan_network_socket():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except:
        local_ip = "192.168.1.1"
    
    print(f"Scanning network from local IP: {local_ip}")
    
    base_ip = '.'.join(local_ip.split('.')[:-1])
    print(f"Scanning range: {base_ip}.1 to {base_ip}.254")
    
    active_devices = []
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            futures[executor.submit(check_host_multiple_ports, ip)] = ip
            
        for future in as_completed(futures):
            ip = futures[future]
            is_online, port = future.result()
            
            if is_online:
                hostname = get_hostname(ip)
                print(f"✅ Found device: {ip} ({hostname}) - responding on port {port}")
                active_devices.append({
                    'ip': ip,
                    'hostname': hostname,
                    'port': port,
                    'status': 'online'
                })
            else:
                hostname = get_hostname(ip)
                if hostname != "Unknown":
                    print(f"⚠️  Device with hostname: {ip} ({hostname}) - no open ports")
    
    return active_devices

if __name__ == "__main__":
    print("=== Socket-based Network Scanner ===")
    devices = scan_network_socket()
    
    print(f"\n=== Summary ===")
    print(f"Found {len(devices)} active devices:")
    for device in devices:
        print(f"  {device['ip']} - {device['hostname']} (port {device['port']})")