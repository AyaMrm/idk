import platform 
import os
import socket
import psutil
import subprocess
import winreg

class SystemInfo:
    def __init__(self):
        self.detailed_platform_info = self.detect_os()
        
    # cette fnct pour detecter quelle OS on a 
    def detect_os(self):
        system = platform.system().lower()
        
        if system == 'windows':
            return self.get_windows_details()
        elif system == 'linux':
            return self.get_linux_details()
        elif system == 'darwin':
            return "MacOS details not implemented" # since on a pas de macOS pour le test ! 
        else:
            return {"system": "unknown", "details": "unknown"}
    
    # avoir les details de chaque os qu'on pourrais avoir 
    def get_windows_details(self):
        #cette facon est via platform module
        version = platform.version()
        release = platform.release()
        
        #via registry pour le precision
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                build_nb = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
        except:
            product_name = f"Windows {release}"
            display_version = version
            build_nb = version
            
        return {
            "System": "Windows", 
            "Version": version,
            "Release": release,
            "Product_Name": product_name,
            "Display_Version": display_version,
            "Build": build_nb,
            "Edition": self.get_windows_edition()
        }
        
    def get_windows_edition(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,  r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                try:
                    edition = winreg.QueryValueEx(key, "EditionID")[0]
                except :
                    edition = winreg.QueryValueEx(key, "ProductName")[0]
                    
            editions_map ={
                'Core': 'Home',
                'Professional': 'Pro',
                'Enterprise': 'Enterprise',
                'Education': 'Education',
                'Ultimate': 'Ultimate'
            }
            return editions_map.get(edition, edition)
        except:
            return "Unkonwn"
        
    def get_linux_details(self):
        try: 
            # vias os release file
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release','r') as f:
                    lines = f.readlines()
                os_info = {}
                for line in lines:
                    if '=' in lines:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                
                return {
                    "System": os_info.get("NANE", "Linux"),
                    "Version": os_info.get("VERSION_ID", "unknown"),
                    "Name": os_info.get("PRETTY_NAME", "Unknown Linux"),
                    "ID": os_info.get("ID", "unknown"),
                    "ID_Like": os_info.get("ID_LIKE", ''),
                    "Version_codename": os_info.get("VERSION_CODENAME", '')
                }
            else:
                return{
                    "System": "Linux",
                    "Version": platform.release(),
                    "Name": "Generic Linux"
                }
        except Exception as e:
            return {
                "System": "Linux",
                "Version": "unknown",
                "error": str(e)
            }