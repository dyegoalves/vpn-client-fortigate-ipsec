# VPN IPsec Client v3

A graphical user interface application for managing IPsec VPN connections on Linux systems built with Qt (PyQt5). This application provides an intuitive interface for connecting to, disconnecting from, and monitoring IPsec VPN connections with excellent integration with Linux desktop environments like Deepin.

## Features

- Qt-based graphical interface for managing VPN connections
- Connection configuration (server address, username, password)
- Connection status monitoring
- Connection logs and status messages
- Connect, disconnect, and status check functionality
- Native look and feel with Linux desktop environments

## Requirements

- Python 3.6 or higher
- PyQt5
- Linux operating system

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

To run the application:

```bash
cd src
python main.py
```

### Configuration

1. Enter the VPN server address
2. Provide your username and password
3. Click "Connect" to establish the VPN connection
4. Use "Disconnect" to terminate the connection
5. Use "Check Status" to view the current connection status

## Application Structure

```
vpn_ipsec_client_v3/
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

The actual VPN connection functionality would need to be implemented using system-level commands (like ipsec, strongswan, or other VPN tools) which would typically require:

- Proper system configuration and VPN client tools
- Administrative privileges for network configuration
- Integration with system services for VPN management

The current implementation includes a simulation of the connection process to demonstrate the Qt GUI functionality.

## License

This project is open source and available under the MIT License.