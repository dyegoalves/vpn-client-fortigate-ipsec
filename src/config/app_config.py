"""
Configuration Module

This file contains all the constants and configuration settings for the VPN IPsec Client application.
"""

import os

# --- Application Info ---
APP_TITLE = "Cliente VPN IPsec Fortigate"
WINDOW_SIZE = (500, 650)

os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- UI Styles (CSS) ---
CONNECTION_STATES = {
    "CONNECTED": "Connected",
    "DISCONNECTED": "Disconnected",
    "CONNECTING": "Connecting...",
    "DISCONNECTING": "Disconnecting...",
    "NOT_CONFIGURED": "Not Configured",
    "NO_CONFIG": "No config",
    "UNAVAILABLE": "Unavailable",
    "ERROR": "Error",
}

# --- Default Messages ---
DEFAULT_MESSAGES = {
    "INIT": "vpn-ipsec-fortigate-client-linux initialized.",
    "CHECKING_CONFIG": "Checking for existing IPsec configurations...",
    "NO_IPSEC": "IPsec is not installed on this system.",
    "NO_CONFIGS": "No IPsec configurations found in system files.",
    "READY": "VPN IPsec Client ready",
}

# --- IPsec Configuration Paths ---
IPSEC_CONFIG_PATHS = ["/etc/ipsec.conf"]
IPSEC_D_PATH = "/etc/ipsec.d/"

# --- Log File ---
# Usar um único arquivo de log organizado dentro de ~/.vpnlogs/
LOGS_DIR = os.path.expanduser("~/.vpnlogs")
os.makedirs(LOGS_DIR, mode=0o755, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOGS_DIR, "vpn_ipsec_client.log")
