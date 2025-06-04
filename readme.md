# Easy Network Manager

A real-time network monitoring tool with GUI for device discovery and network statistics visualization.

## Features

- **Device Discovery**: Scans local network and tracks device status
- **Multiple Scan Methods**: Auto-detects best method (ping/socket/hybrid)
- **Real-time Monitoring**: Live bandwidth and packet transmission graphs  
- **Network Interface Info**: View interface details and IP configurations
- **Start/Stop Controls**: Manual control over monitoring processes

## Installation

```bash
git clone https://github.com/astrotaca/EasyNetworkManager.git
cd EasyNetworkManager
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.7+
- psutil >= 5.9.0
- matplotlib >= 3.5.0

## Usage

1. **Start the application**: `python main.py`
2. **Click "Start Monitoring"** to begin automatic network scanning
3. **View devices** in the Devices tab
4. **Monitor network stats** in real-time graphs
5. **Check interfaces** for network configuration details

## Configuration

Modify `config.py` to adjust:
- Scan intervals and timeouts
- Thread counts for scanning
- Network ranges and ports

## Testing

The `tests/` folder contains diagnostic tools:
- `test_scan.py` - Debug ping connectivity
- `socket_scanner.py` - Alternative socket-based scanning

## Architecture

- `main.py` - Application entry point and coordination
- `network_monitor.py` - Core scanning and network functionality
- `gui.py` - GUI interface with matplotlib visualization
- `data_handler.py` - Thread-safe data management
- `config.py` - Configuration settings

## Compatibility

- Windows, Linux, macOS
- Works with most home and office networks
- Auto-detects best scanning method for environment

## License

MIT License
