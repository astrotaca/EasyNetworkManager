import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import threading
import time

class NetworkMonitorGUI:
    def __init__(self, data_handler, network_monitor, app):
        self.data_handler = data_handler
        self.network_monitor = network_monitor
        self.app = app
        self.root = tk.Tk()
        self.root.title("Easy Network Manager")
        self.root.geometry("1200x800")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.monitoring_active = False
        self.setup_gui()
        self.start_auto_refresh()
        
    def setup_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.devices_frame = ttk.Frame(self.notebook)
        self.stats_frame = ttk.Frame(self.notebook)
        self.interfaces_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.devices_frame, text="Devices")
        self.notebook.add(self.stats_frame, text="Network Stats")
        self.notebook.add(self.interfaces_frame, text="Interfaces")
        
        self.setup_devices_tab()
        self.setup_stats_tab()
        self.setup_interfaces_tab()
        
        self.setup_status_bar()
        
    def setup_devices_tab(self):
        control_frame = ttk.Frame(self.devices_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", 
                                     command=self.start_monitoring, style="Accent.TButton")
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", 
                                    command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Separator(control_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        self.scan_button = ttk.Button(control_frame, text="Scan Network", 
                                    command=self.manual_scan)
        self.scan_button.pack(side='left', padx=5)
        
        self.refresh_button = ttk.Button(control_frame, text="Refresh", 
                                       command=self.refresh_devices)
        self.refresh_button.pack(side='left', padx=5)
        
        method_info = self.network_monitor.get_scan_method_info()
        
        ttk.Label(control_frame, text="Method:").pack(side='left', padx=(20,5))
        self.scan_method_var = tk.StringVar(value=method_info['method'])
        method_combo = ttk.Combobox(control_frame, textvariable=self.scan_method_var,
                                  values=list(method_info['available_methods'].keys()),
                                  state='readonly', width=10)
        method_combo.pack(side='left', padx=5)
        method_combo.bind('<<ComboboxSelected>>', self.on_scan_method_change)
        
        columns = ('IP', 'Hostname', 'Status', 'Ping (ms)', 'Method', 'Last Seen')
        self.devices_tree = ttk.Treeview(self.devices_frame, columns=columns, show='headings')
        
        column_widths = {'IP': 120, 'Hostname': 150, 'Status': 80, 'Ping (ms)': 80, 'Method': 100, 'Last Seen': 120}
        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=column_widths.get(col, 100))
            
        devices_scrollbar = ttk.Scrollbar(self.devices_frame, orient='vertical', 
                                        command=self.devices_tree.yview)
        self.devices_tree.configure(yscrollcommand=devices_scrollbar.set)
        
        devices_frame_container = ttk.Frame(self.devices_frame)
        devices_frame_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.devices_tree.pack(side='left', fill='both', expand=True)
        devices_scrollbar.pack(side='right', fill='y')
        
    def setup_stats_tab(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.ax1.set_title('Network Bandwidth (Bytes/sec)')
        self.ax1.set_ylabel('Bytes/sec')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_title('Network Packets (Packets/sec)')
        self.ax2.set_ylabel('Packets/sec')
        self.ax2.set_xlabel('Time (seconds ago)')
        self.ax2.grid(True, alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.stats_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.anim = FuncAnimation(self.fig, self.update_plots, interval=2000, blit=False, cache_frame_data=False)
        
    def setup_interfaces_tab(self):
        int_columns = ('Interface', 'IP Address', 'Netmask', 'Broadcast')
        self.interfaces_tree = ttk.Treeview(self.interfaces_frame, columns=int_columns, show='headings')
        
        for col in int_columns:
            self.interfaces_tree.heading(col, text=col)
            self.interfaces_tree.column(col, width=200)
            
        self.interfaces_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(self.interfaces_frame, text="Refresh Interfaces", 
                  command=self.refresh_interfaces).pack(pady=5)
                  
    def setup_status_bar(self):
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(self.status_frame, text="Ready - Click 'Start Monitoring' to begin")
        self.status_label.pack(side='left', padx=5)
        
        self.monitoring_status_label = ttk.Label(self.status_frame, text="⏸️ Stopped", foreground='red')
        self.monitoring_status_label.pack(side='left', padx=10)
        
        method_info = self.network_monitor.get_scan_method_info()
        self.scan_method_label = ttk.Label(self.status_frame, 
                                         text=f"Scan: {method_info['method']}")
        self.scan_method_label.pack(side='left', padx=10)
        
        self.device_count_label = ttk.Label(self.status_frame, text="Devices: 0")
        self.device_count_label.pack(side='right', padx=5)
        
    def start_monitoring(self):
        self.app.start_monitoring()
        self.monitoring_active = True
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.monitoring_status_label.config(text="▶️ Running", foreground='green')
        self.update_status("Network monitoring started")
        
    def stop_monitoring(self):
        self.app.stop_monitoring()
        self.monitoring_active = False
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.monitoring_status_label.config(text="⏸️ Stopped", foreground='red')
        self.update_status("Network monitoring stopped")
        
    def on_scan_method_change(self, event=None):
        new_method = self.scan_method_var.get()
        if self.network_monitor.change_scan_method(new_method):
            self.scan_method_label.config(text=f"Scan: {new_method}")
            self.update_status(f"Scan method changed to {new_method}")
        
    def manual_scan(self):
        self.update_status("Scanning network...")
        self.scan_button.config(state='disabled')
        threading.Thread(target=self._scan_thread, daemon=True).start()
        
    def _scan_thread(self):
        try:
            self.network_monitor.scan_network()
            self.root.after(0, lambda: self.update_status("Scan completed"))
            self.root.after(0, self.refresh_devices)
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Scan failed: {e}"))
        finally:
            self.root.after(0, lambda: self.scan_button.config(state='normal'))
            
    def refresh_devices(self):
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
            
        devices = self.data_handler.get_devices()
        for device in devices:
            last_seen = time.strftime('%H:%M:%S', time.localtime(device['last_seen']))
            ping_str = f"{device['ping_time']:.1f}" if device['ping_time'] else "N/A"
            
            method_info = device.get('scan_method', 'unknown')
            if device.get('extra_info'):
                method_info += f" ({device['extra_info']})"
            
            tags = ('online',) if device['status'] == 'online' else ('offline',)
            
            self.devices_tree.insert('', 'end', values=(
                device['ip'],
                device['hostname'],
                device['status'].title(),
                ping_str,
                method_info,
                last_seen
            ), tags=tags)
            
        self.devices_tree.tag_configure('online', foreground='green')
        self.devices_tree.tag_configure('offline', foreground='red')
        
        online_count = len([d for d in devices if d['status'] == 'online'])
        self.device_count_label.config(text=f"Devices: {len(devices)} ({online_count} online)")
        
    def refresh_interfaces(self):
        for item in self.interfaces_tree.get_children():
            self.interfaces_tree.delete(item)
            
        interfaces = self.network_monitor.get_interface_info()
        for interface in interfaces:
            for addr in interface['addresses']:
                self.interfaces_tree.insert('', 'end', values=(
                    interface['name'],
                    addr['ip'],
                    addr['netmask'],
                    addr.get('broadcast', 'N/A')
                ))
                
    def update_plots(self, frame):
        try:
            rates = self.data_handler.calculate_network_rates()
            history = self.data_handler.get_stats_history(60)
            
            if not history:
                return
                
            times = [-(len(history) - i - 1) * 5 for i in range(len(history))]
            bytes_sent = [stats.get('bytes_sent_rate', 0) for stats in history]
            bytes_recv = [stats.get('bytes_recv_rate', 0) for stats in history]
            packets_sent = [stats.get('packets_sent_rate', 0) for stats in history]
            packets_recv = [stats.get('packets_recv_rate', 0) for stats in history]
            
            self.ax1.clear()
            self.ax1.plot(times, bytes_sent, label='Sent', color='red', linewidth=2)
            self.ax1.plot(times, bytes_recv, label='Received', color='blue', linewidth=2)
            self.ax1.set_title('Network Bandwidth (Bytes/sec)')
            self.ax1.set_ylabel('Bytes/sec')
            self.ax1.legend()
            self.ax1.grid(True, alpha=0.3)
            
            self.ax2.clear()
            self.ax2.plot(times, packets_sent, label='Sent', color='red', linewidth=2)
            self.ax2.plot(times, packets_recv, label='Received', color='blue', linewidth=2)
            self.ax2.set_title('Network Packets (Packets/sec)')
            self.ax2.set_ylabel('Packets/sec')
            self.ax2.set_xlabel('Time (seconds ago)')
            self.ax2.legend()
            self.ax2.grid(True, alpha=0.3)
            
            self.fig.tight_layout()
            
        except Exception as e:
            print(f"Plot update error: {e}")
            
    def start_auto_refresh(self):
        def auto_refresh():
            if self.monitoring_active:
                self.refresh_devices()
            self.refresh_interfaces()
            self.root.after(10000, auto_refresh)
            
        self.root.after(1000, auto_refresh)
        
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def on_closing(self):
        if self.monitoring_active:
            if messagebox.askokcancel("Quit", "Stop monitoring and close Easy Network Manager?"):
                self.stop_monitoring()
                self.app.stop()
            else:
                return
        else:
            self.app.stop()
        
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()