class Config:
    
    SCANNING_METHODS = {
        'ping': 'Use ICMP ping (traditional method)',
        'socket': 'Use socket connections to common ports',
        'hybrid': 'Try ping first, fallback to socket',
        'auto': 'Automatically detect best method'
    }
    
    DEFAULT_SCAN_METHOD = 'auto'
    
    PING_TIMEOUT = 3
    PING_COUNT = 1
    
    SOCKET_TIMEOUT = 1
    COMMON_PORTS = [80, 443, 22, 23, 53, 135, 139, 445, 3389, 8080, 21, 25, 110, 993, 995]
    SOCKET_THREADS = 30
    
    MAX_SCAN_THREADS = 50
    MAX_STATUS_THREADS = 20
    
    SCAN_INTERVAL = 30
    STATUS_UPDATE_INTERVAL = 5
    STATS_UPDATE_INTERVAL = 5
    GUI_REFRESH_INTERVAL = 10
    
    MAX_STATS_HISTORY = 300
    DEVICE_OFFLINE_TIMEOUT = 300
    
    DEFAULT_NETWORK_MASK = '255.255.255.0'
    SCAN_RANGE_START = 1
    SCAN_RANGE_END = 254
    
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    PLOT_UPDATE_INTERVAL = 2000
    
    COLORS = {
        'online': 'green',
        'offline': 'red',
        'unknown': 'orange',
        'sent': 'red',
        'received': 'blue'
    }
    
    PORT_SERVICES = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        135: 'RPC',
        139: 'NetBIOS',
        443: 'HTTPS',
        445: 'SMB',
        993: 'IMAPS',
        995: 'POP3S',
        3389: 'RDP',
        8080: 'HTTP-Alt'
    }
    
    @classmethod
    def get_scan_timeout(cls):
        return cls.PING_TIMEOUT
        
    @classmethod
    def get_thread_count(cls):
        return cls.MAX_SCAN_THREADS
        
    @classmethod
    def get_socket_timeout(cls):
        return cls.SOCKET_TIMEOUT
        
    @classmethod
    def get_service_name(cls, port):
        return cls.PORT_SERVICES.get(port, f'Port {port}')