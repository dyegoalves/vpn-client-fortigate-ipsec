# vpn-ipsec-fortigate-client-linux

A graphical user interface application for managing IPsec VPN connections on Linux systems built with Qt (PySide6). This application provides an intuitive interface for connecting to, disconnecting from, and monitoring IPsec VPN connections with excellent integration with Linux desktop environments like Deepin.

## Features

- Qt-based graphical interface for managing VPN connections
- Connection configuration with automatic detection of available IPsec connections
- Detailed connection information (server address, authentication type, IKE/ESP protocols, remote subnet)
- Connection status monitoring with visual indicators (red/green toggle switch)
- Connection logs with reduced UI output and file logging when connected
- Connect, disconnect, and status check functionality
- System theme integration (light/dark mode support)
- Deepin desktop environment compatibility
- Detailed connection details display

## Requirements

- Python 3.6 or higher
- PySide6
- Linux operating system with IPsec utilities (strongswan or libreswan)
- Administrative privileges for IPsec connection management

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install --break-system-packages -r requirements.txt  # or use a virtual environment
```

## Usage

To run the application:

```bash
cd src
python main.py
```

### Configuration

1. The application automatically detects available IPsec connections from `/etc/ipsec.conf` and `/etc/ipsec.d/*.conf`
2. Select the desired connection from the dropdown menu
3. View connection details (server address, authentication type, protocols, etc.)
4. Use the toggle switch or connect/disconnect buttons to control the VPN connection
5. Monitor connection status and logs in the interface
6. Access detailed logs through the "Ver Logs Detalhados" button

## Application Structure

```
vpn-ipsec-fortigate-client-linux/
├── README.md
├── requirements.txt
└── src/
    └── main.py
```

## Implementation Notes

This is a Qt GUI frontend for a VPN IPsec client. Qt was chosen for its excellent integration with Linux desktop environments, particularly Deepin, providing:

- Native look and feel that matches the system theme
- Better integration with desktop environment features
- Improved visual consistency across different Linux distributions

The application integrates with system-level IPsec commands (ipsec up/down/status) to manage connections and includes:

- Proper system configuration for Deepin compatibility (xcb platform)
- Automatic theme detection and dark mode support
- Toggle switch with color-coding (red for disconnected, green for connected)
- File-based logging that only saves when connected
- Reduced visual log output in the interface as requested

## License

This project is open source and available under the MIT License.