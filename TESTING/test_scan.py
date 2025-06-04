#!/usr/bin/env python3

import subprocess
import socket
import platform

def test_ping(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-W', '1000', ip]
    
    print(f"Testing ping to {ip}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        print(f"Return code: {result.returncode}")
        if result.returncode == 0:
            print("SUCCESS: Ping worked!")
            print(f"Output: {result.stdout[:200]}")
        else:
            print("FAILED: Ping failed")
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def main():
    print("=== Network Scan Debug Test ===")
    local_ip = get_local_ip()
    print(f"Local IP: {local_ip}")

    print("\n--- Testing ping to self ---")
    test_ping(local_ip)

    router_ip = '.'.join(local_ip.split('.')[:-1]) + '.1'
    print(f"\n--- Testing ping to likely router: {router_ip} ---")
    test_ping(router_ip)

    print(f"\n--- Testing ping to a few other IPs on your network ---")
    base_ip = '.'.join(local_ip.split('.')[:-1])
    for i in [2, 10, 20, 100]:
        test_ip = f"{base_ip}.{i}"
        print(f"\n--- Testing {test_ip} ---")
        test_ping(test_ip)
        
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()