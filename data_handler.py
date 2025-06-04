import time
import threading
from collections import deque

class DataHandler:
    def __init__(self):
        self.devices = []
        self.network_stats_history = deque(maxlen=300)
        self.lock = threading.Lock()
        self.last_network_stats = None
        
    def update_devices(self, new_devices):
        with self.lock:
            existing_devices = {device['ip']: device for device in self.devices}
            
            updated_devices = []
            for new_device in new_devices:
                ip = new_device['ip']
                if ip in existing_devices:
                    existing_device = existing_devices[ip]
                    existing_device.update(new_device)
                    updated_devices.append(existing_device)
                else:
                    updated_devices.append(new_device)
                    
            for existing_device in self.devices:
                if existing_device['ip'] not in [d['ip'] for d in new_devices]:
                    time_since_seen = time.time() - existing_device['last_seen']
                    if time_since_seen < 300:
                        existing_device['status'] = 'offline'
                        if existing_device not in updated_devices:
                            updated_devices.append(existing_device)
                            
            self.devices = updated_devices
            
    def update_device_list(self, devices):
        with self.lock:
            self.devices = devices.copy()
            
    def get_devices(self):
        with self.lock:
            return self.devices.copy()
            
    def add_network_stats(self, stats):
        with self.lock:
            if self.last_network_stats:
                time_delta = stats['timestamp'] - self.last_network_stats['timestamp']
                if time_delta > 0:
                    stats['bytes_sent_rate'] = (stats['bytes_sent'] - self.last_network_stats['bytes_sent']) / time_delta
                    stats['bytes_recv_rate'] = (stats['bytes_recv'] - self.last_network_stats['bytes_recv']) / time_delta
                    stats['packets_sent_rate'] = (stats['packets_sent'] - self.last_network_stats['packets_sent']) / time_delta
                    stats['packets_recv_rate'] = (stats['packets_recv'] - self.last_network_stats['packets_recv']) / time_delta
                else:
                    stats['bytes_sent_rate'] = 0
                    stats['bytes_recv_rate'] = 0
                    stats['packets_sent_rate'] = 0
                    stats['packets_recv_rate'] = 0
            else:
                stats['bytes_sent_rate'] = 0
                stats['bytes_recv_rate'] = 0
                stats['packets_sent_rate'] = 0
                stats['packets_recv_rate'] = 0
                
            self.network_stats_history.append(stats)
            self.last_network_stats = stats
            
    def get_stats_history(self, count=None):
        with self.lock:
            if count is None:
                return list(self.network_stats_history)
            else:
                return list(self.network_stats_history)[-count:]
                
    def calculate_network_rates(self):
        with self.lock:
            if len(self.network_stats_history) < 2:
                return {
                    'bytes_sent_rate': 0,
                    'bytes_recv_rate': 0,
                    'packets_sent_rate': 0,
                    'packets_recv_rate': 0
                }
                
            latest = self.network_stats_history[-1]
            return {
                'bytes_sent_rate': latest.get('bytes_sent_rate', 0),
                'bytes_recv_rate': latest.get('bytes_recv_rate', 0),
                'packets_sent_rate': latest.get('packets_sent_rate', 0),
                'packets_recv_rate': latest.get('packets_recv_rate', 0),
                'total_bytes_sent': latest['bytes_sent'],
                'total_bytes_recv': latest['bytes_recv'],
                'total_packets_sent': latest['packets_sent'],
                'total_packets_recv': latest['packets_recv']
            }
            
    def get_device_by_ip(self, ip):
        with self.lock:
            for device in self.devices:
                if device['ip'] == ip:
                    return device.copy()
            return None
            
    def get_online_devices(self):
        with self.lock:
            return [device.copy() for device in self.devices if device['status'] == 'online']
            
    def get_device_count(self):
        with self.lock:
            return len(self.devices)
            
    def get_online_device_count(self):
        with self.lock:
            return len([device for device in self.devices if device['status'] == 'online'])
            
    def clear_history(self):
        with self.lock:
            self.network_stats_history.clear()
            self.last_network_stats = None
            
    def format_bytes(self, bytes_value):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
        
    def get_summary_stats(self):
        with self.lock:
            rates = self.calculate_network_rates()
            return {
                'total_devices': self.get_device_count(),
                'online_devices': self.get_online_device_count(),
                'bytes_sent_rate': self.format_bytes(rates['bytes_sent_rate']),
                'bytes_recv_rate': self.format_bytes(rates['bytes_recv_rate']),
                'total_bytes_sent': self.format_bytes(rates.get('total_bytes_sent', 0)),
                'total_bytes_recv': self.format_bytes(rates.get('total_bytes_recv', 0))
            }