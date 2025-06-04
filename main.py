#!/usr/bin/env python3

import sys
import threading
import time
import signal
from gui import NetworkMonitorGUI
from network_monitor import NetworkMonitor
from data_handler import DataHandler

class NetworkMonitorApp:
    def __init__(self):
        self.data_handler = DataHandler()
        self.network_monitor = NetworkMonitor(self.data_handler)
        self.gui = NetworkMonitorGUI(self.data_handler, self.network_monitor, self)
        self.running = True
        self.monitor_thread = None
        
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        print("\nReceived interrupt signal, shutting down...")
        self.stop()
        sys.exit(0)
        
    def start_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Network monitoring started")
        
    def stop_monitoring(self):
        self.running = False
        if self.monitor_thread:
            print("Stopping network monitoring...")
            self.monitor_thread.join(timeout=2)
        print("Network monitoring stopped")
        
    def _monitor_loop(self):
        scan_counter = 0
        
        while self.running:
            try:
                if scan_counter % 6 == 0:
                    if self.running:
                        self.network_monitor.scan_network()
                
                if self.running:
                    self.network_monitor.update_device_status()
                    
                if self.running:
                    self.network_monitor.collect_network_stats()
                
                scan_counter += 1
                
                for _ in range(50):
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                if self.running:
                    print(f"Monitoring error: {e}")
                    time.sleep(10)
                
        print("Monitor loop exited")
                
    def stop(self):
        print("Shutting down Easy Network Manager...")
        self.stop_monitoring()
        if hasattr(self, 'gui') and self.gui:
            try:
                self.gui.root.quit()
                self.gui.root.destroy()
            except:
                pass
        
    def run(self):
        try:
            self.start_monitoring()
            self.gui.run()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self.stop()

if __name__ == "__main__":
    try:
        app = NetworkMonitorApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)