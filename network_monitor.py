import subprocess
import socket
import psutil
import ipaddress
import time
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config

class NetworkMonitor:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.config = Config()
        self.local_ip = self._get_local_ip()
        self.network_range = self._get_network_range()
        self.scan_method = self._detect_best_scan_method()
        
        print(f"Network Monitor initialized:")
        print(f"  Local IP: {self.local_ip}")
        print(f"  Scan method: {self.scan_method}")
        
    def _get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
            
    def _get_network_range(self):
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address == self.local_ip:
                        network = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                        return str(network.network_address), str(network.netmask)
            return self.local_ip.rsplit('.', 1)[0] + '.0', '255.255.255.0'
        except:
            return self.local_ip.rsplit('.', 1)[0] + '.0', '255.255.255.0'
    
    def _detect_best_scan_method(self):
        if self.config.DEFAULT_SCAN_METHOD != 'auto':
            return self.config.DEFAULT_SCAN_METHOD
            
        print("Auto-detecting best scan method...")
        
        ping_works = self._test_ping_method()
        socket_works = self._test_socket_method()
        
        if ping_works and socket_works:
            print("Both ping and socket methods work - using hybrid")
            return 'hybrid'
        elif ping_works:
            print("Ping method works - using ping")
            return 'ping'
        elif socket_works:
            print("Socket method works - using socket")
            return 'socket'
        else:
            print("No methods work reliably - using socket as fallback")
            return 'socket'
    
    def _test_ping_method(self):
        try:
            return self._ping_host(self.local_ip) is not None
        except:
            return False
    
    def _test_socket_method(self):
        try:
            return self._socket_check_host(self.local_ip)
        except:
            return False
            
    def _ping_host(self, ip):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-W', '1000', ip]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'time=' in output:
                    time_str = output.split('time=')[1].split()[0]
                    return float(time_str.replace('ms', ''))
                return 1.0
            return None
        except:
            return None
    
    def _socket_check_host(self, ip, timeout=None):
        if timeout is None:
            timeout = self.config.get_socket_timeout()
            
        for port in self.config.COMMON_PORTS[:5]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        return port
            except:
                continue
        return None
    
    def _hybrid_check_host(self, ip):
        ping_result = self._ping_host(ip)
        if ping_result is not None:
            return ping_result
        
        socket_result = self._socket_check_host(ip)
        if socket_result is not None:
            return 1.0
        
        return None
            
    def _get_hostname(self, ip):
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname if hostname != ip else "Unknown"
        except:
            return "Unknown"
            
    def _scan_ip_range(self, start_ip, end_ip):
        base_ip = '.'.join(start_ip.split('.')[:-1])
        start_num = int(start_ip.split('.')[-1])
        end_num = int(end_ip.split('.')[-1])
        
        active_devices = []
        
        if self.scan_method == 'ping':
            check_func = self._ping_host
            max_workers = self.config.MAX_SCAN_THREADS
        elif self.scan_method == 'socket':
            check_func = self._socket_check_host
            max_workers = self.config.SOCKET_THREADS
        elif self.scan_method == 'hybrid':
            check_func = self._hybrid_check_host
            max_workers = self.config.SOCKET_THREADS
        else:
            check_func = self._socket_check_host
            max_workers = self.config.SOCKET_THREADS
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for i in range(start_num, end_num + 1):
                ip = f"{base_ip}.{i}"
                futures[executor.submit(check_func, ip)] = ip
                
            for future in as_completed(futures):
                ip = futures[future]
                result = future.result()
                
                if result is not None:
                    hostname = self._get_hostname(ip)
                    
                    if self.scan_method == 'socket' and isinstance(result, int):
                        service = self.config.get_service_name(result)
                        ping_time = 1.0
                        extra_info = f"Port {result} ({service})"
                    else:
                        ping_time = result if isinstance(result, float) else 1.0
                        extra_info = None
                    
                    device = {
                        'ip': ip,
                        'hostname': hostname,
                        'ping_time': ping_time,
                        'status': 'online',
                        'last_seen': time.time(),
                        'scan_method': self.scan_method,
                        'extra_info': extra_info
                    }
                    active_devices.append(device)
                    
        return active_devices
        
    def scan_network(self):
        print(f"Scanning network using {self.scan_method} method...")
        network_base = '.'.join(self.local_ip.split('.')[:-1])
        start_ip = f"{network_base}.1"
        end_ip = f"{network_base}.254"
        
        devices = self._scan_ip_range(start_ip, end_ip)
        print(f"Found {len(devices)} active devices")
        self.data_handler.update_devices(devices)
        
    def update_device_status(self):
        devices = self.data_handler.get_devices()
        
        if not devices:
            return
        
        if self.scan_method == 'ping':
            check_func = self._ping_host
            max_workers = self.config.MAX_STATUS_THREADS
        elif self.scan_method == 'socket':
            check_func = self._socket_check_host  
            max_workers = min(self.config.MAX_STATUS_THREADS, 10)
        else:
            check_func = self._hybrid_check_host
            max_workers = min(self.config.MAX_STATUS_THREADS, 10)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for device in devices:
                futures[executor.submit(check_func, device['ip'])] = device
                
            for future in as_completed(futures):
                device = futures[future]
                result = future.result()
                
                if result is not None:
                    device['ping_time'] = result if isinstance(result, float) else 1.0
                    device['status'] = 'online'
                    device['last_seen'] = time.time()
                else:
                    device['status'] = 'offline'
                    
        self.data_handler.update_device_list(devices)
        
    def collect_network_stats(self):
        stats = psutil.net_io_counters()
        
        network_stats = {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv,
            'timestamp': time.time()
        }
        
        self.data_handler.add_network_stats(network_stats)
        
    def get_interface_info(self):
        interfaces = []
        
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface,
                'addresses': []
            }
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interface_info['addresses'].append({
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                    
            if interface_info['addresses']:
                interfaces.append(interface_info)
                
        return interfaces
        
    def get_network_usage(self):
        return self.data_handler.calculate_network_rates()
        
    def get_scan_method_info(self):
        return {
            'method': self.scan_method,
            'description': self.config.SCANNING_METHODS.get(self.scan_method, 'Unknown'),
            'available_methods': self.config.SCANNING_METHODS
        }
        
    def change_scan_method(self, method):
        if method in self.config.SCANNING_METHODS:
            self.scan_method = method
            print(f"Scanning method changed to: {method}")
            return True
        return False