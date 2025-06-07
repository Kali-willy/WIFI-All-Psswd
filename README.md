# WIFI-All-Psswd
📋 Description:  This script helps you recover all previously connected WiFi passwords that your device has stored. If you've ever connected to a WiFi network before, this tool will show you:      📶 The name of each WiFi network (SSID)      🔑 The saved password (if available)

It supports all major operating systems:

    ✅ Linux (Ubuntu, Kali, Debian, Arch, etc.)

    ✅ Windows (via Command Prompt, PowerShell, or WSL)

    ✅ macOS (MacBook, iMac, etc.)

    # WiFi Password Extractor

This script extracts and saves WiFi passwords from all previously connected networks on Linux, Windows, and macOS systems.

## Usage

1. Make sure you have Python 3 installed on your system.
2. Run the script with appropriate permissions:

### Linux
```
sudo python3 wifi_passwords.py
```

### Windows
Run Command Prompt as Administrator:
```
python wifi_passwords.py
```

### macOS
```
python3 wifi_passwords.py
```
Note: For some macOS networks, the script will list network names but you may need to manually retrieve passwords by running the suggested command in Terminal.

## Output

The script creates a text file named `wifi-txt` containing all your saved WiFi networks and their passwords.

## Features

- Recovers passwords from all previously connected WiFi networks
- Works on Linux, Windows, and macOS
- Multiple password recovery methods for maximum success rate
- No need to know the passwords beforehand

## Requirements

- Python 3
- Administrator/sudo privileges (to access password information) 
