#!/usr/bin/env python3
import os
import platform
import subprocess
import re
from datetime import datetime

def get_windows_wifi_passwords():
    passwords = []
    
    # Get all WiFi profiles
    wifi_profiles = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True, check=False).stdout
    
    # Extract profile names
    profile_names = re.findall(r"All User Profile\s+:\s+(.*)", wifi_profiles)
    
    # For each profile, get the password
    for name in profile_names:
        # Clean the name
        name = name.strip()
        
        # Get details for this profile
        wifi_info = subprocess.run(['netsh', 'wlan', 'show', 'profile', name, 'key=clear'], 
                                  capture_output=True, text=True, check=False).stdout
        
        # Extract password
        password = re.search(r"Key Content\s+:\s+(.*)", wifi_info)
        
        if password:
            passwords.append(f"Network: {name}\nPassword: {password.group(1)}\n")
        else:
            passwords.append(f"Network: {name}\nPassword: Not found\n")
    
    return passwords

def get_linux_wifi_passwords():
    passwords = []
    
    # Method 1: NetworkManager
    nm_path = "/etc/NetworkManager/system-connections/"
    if os.path.exists(nm_path):
        try:
            connection_files = os.listdir(nm_path)
            for file in connection_files:
                file_path = os.path.join(nm_path, file)
                try:
                    # We need sudo to read these files
                    output = subprocess.run(['sudo', 'cat', file_path], 
                                          capture_output=True, text=True, check=False).stdout
                    
                    # Extract SSID
                    ssid_match = re.search(r"ssid=(.*)", output)
                    ssid = ssid_match.group(1) if ssid_match else file
                    
                    # Extract password
                    psk_match = re.search(r"psk=(.*)", output)
                    password = psk_match.group(1) if psk_match else "Not found"
                    
                    passwords.append(f"Network: {ssid}\nPassword: {password}\n")
                except Exception as e:
                    passwords.append(f"Error reading {file}: {str(e)}\n")
        except PermissionError:
            passwords.append("Permission denied for NetworkManager files: Try running with sudo\n")
    
    # Method 2: Try to use nmcli (newer systems)
    try:
        output = subprocess.run(['sudo', 'nmcli', '-g', 'NAME,802-11-wireless-security.psk', 'connection', 'show'], 
                               capture_output=True, text=True, check=False).stdout
        connections = output.strip().split('\n')
        
        for conn in connections:
            if ':' in conn:
                parts = conn.split(':')
                if len(parts) >= 2:
                    ssid = parts[0]
                    password = parts[1]
                    passwords.append(f"Network (nmcli): {ssid}\nPassword: {password}\n")
    except Exception as e:
        passwords.append(f"Error using nmcli: {str(e)}\n")
    
    # Method 3: Check wpa_supplicant.conf (older systems)
    wpa_paths = ['/etc/wpa_supplicant/wpa_supplicant.conf', '/etc/wpa_supplicant.conf']
    for wpa_path in wpa_paths:
        if os.path.exists(wpa_path):
            try:
                output = subprocess.run(['sudo', 'cat', wpa_path], 
                                      capture_output=True, text=True, check=False).stdout
                
                # Find network blocks
                network_blocks = re.findall(r'network=\{(.*?)\}', output, re.DOTALL)
                
                for block in network_blocks:
                    ssid_match = re.search(r'ssid="(.*?)"', block)
                    ssid = ssid_match.group(1) if ssid_match else "Unknown"
                    
                    psk_match = re.search(r'psk="(.*?)"', block)
                    password = psk_match.group(1) if psk_match else "Not found"
                    
                    passwords.append(f"Network (wpa): {ssid}\nPassword: {password}\n")
            except Exception as e:
                passwords.append(f"Error reading {wpa_path}: {str(e)}\n")
    
    if not passwords:
        passwords.append("No WiFi passwords found. Try running with sudo privileges.\n")
    
    return passwords

def get_macos_wifi_passwords():
    passwords = []
    
    try:
        # Get list of preferred networks
        networks_output = subprocess.run(['networksetup', '-listallnetworkservices'], 
                                       capture_output=True, text=True, check=False).stdout
        
        # Get preferred wireless networks
        preferred_output = subprocess.run(['defaults', 'read', '/Library/Preferences/SystemConfiguration/com.apple.airport.preferences', 'RememberedNetworks'], 
                                        capture_output=True, text=True, check=False).stdout
        
        if "does not exist" not in preferred_output:
            # Extract SSIDs from the output
            ssids = re.findall(r'SSIDString = "(.*?)";', preferred_output)
            
            for ssid in ssids:
                # Try to get the password
                try:
                    password_output = subprocess.run(['security', 'find-generic-password', '-D', 'AirPort network password', '-a', ssid, '-w'], 
                                                  capture_output=True, text=True, check=False).stdout.strip()
                    
                    if password_output:
                        passwords.append(f"Network: {ssid}\nPassword: {password_output}\n")
                    else:
                        # Alternative method with user interaction
                        passwords.append(f"Network: {ssid}\nPassword: Run 'security find-generic-password -wa \"{ssid}\"' in Terminal\n")
                except Exception as e:
                    passwords.append(f"Network: {ssid}\nPassword: Run 'security find-generic-password -wa \"{ssid}\"' in Terminal\n")
        
        if not ssids:
            # Try alternative method using airport utility
            airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if os.path.exists(airport):
                networks = subprocess.run([airport, '--getprefs'], 
                                        capture_output=True, text=True, check=False).stdout
                
                preferred_networks = re.findall(r"Preferred networks:(.*?)(?:\n\n|\Z)", networks, re.DOTALL)
                if preferred_networks:
                    network_list = re.findall(r"\d+: (.+)", preferred_networks[0])
                    
                    for network in network_list:
                        passwords.append(f"Network: {network}\nPassword: Run 'security find-generic-password -wa \"{network}\"' in Terminal\n")
    except Exception as e:
        passwords.append(f"Error retrieving macOS WiFi networks: {str(e)}\n")
    
    if not passwords:
        passwords.append("No WiFi networks found or unable to access them without proper permissions.\n")
    
    return passwords

def main():
    system = platform.system()
    
    print(f"Extracting WiFi passwords on {system}...")
    
    if system == "Windows":
        passwords = get_windows_wifi_passwords()
    elif system == "Linux":
        passwords = get_linux_wifi_passwords()
    elif system == "Darwin":  # macOS
        passwords = get_macos_wifi_passwords()
    else:
        print(f"Unsupported operating system: {system}")
        return
    
    # Create output file
    filename = "wifi-txt"
    
    with open(filename, "w") as f:
        f.write(f"WiFi Passwords extracted on {system} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("="*50 + "\n\n")
        for entry in passwords:
            f.write(entry)
            f.write("-"*30 + "\n")
    
    print(f"WiFi passwords saved to {filename}")
    print(f"Total networks found: {len(passwords)}")

if __name__ == "__main__":
    main() 