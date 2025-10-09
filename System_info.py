import platform 
import os
import socket
import psutil
import subprocess
#import winreg
import datetime

class SystemInfo:
    def __init__(self):
        self.detailed_platform_info = self.detect_os()
        #self.architecture = self.detect_architecture()
        
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
    
    
    # avoir les details de chaque os qu'on pourrais avoir (marche)
    def get_windows_details(self):
        import winreg
        import platform
        from datetime import datetime
    
        version = platform.version()
        release = platform.release()
        architecture = platform.machine()
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                build_nb = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                try:
                    display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                except FileNotFoundError:
                    display_version = ""
                
                try:
                    edition = winreg.QueryValueEx(key, "EditionID")[0]
                except FileNotFoundError:
                    edition = ""
                
                try:
                    product_id = winreg.QueryValueEx(key, "ProductName")[0].split(' ')[0] + " " + winreg.QueryValueEx(key, "ProductName")[0].split(' ')[1]
                except:
                    product_id = "Windows"
    
                id_like = "Windows NT"
                
    
                try:
                    version_codename = winreg.QueryValueEx(key, "ReleaseId")[0]  
                except FileNotFoundError:
                    version_codename = display_version if display_version else ""
                
                try:
                    registered_owner = winreg.QueryValueEx(key, "RegisteredOwner")[0]
                except FileNotFoundError:
                    registered_owner = ""
                
                try:
                    install_date = winreg.QueryValueEx(key, "InstallDate")[0]
                    if install_date:
                        install_date = datetime.fromtimestamp(install_date).strftime('%Y-%m-%d')
                except FileNotFoundError:
                    install_date = ""
                
                try:
                    product_type = winreg.QueryValueEx(key, "ProductType")[0]
                    system_type = "Server" if product_type == "Server" else "Client"
                except FileNotFoundError:
                    system_type = "Client"
                
        except Exception as reg_error:
            product_name = "Windows"
            build_nb = release
            display_version = ""
            edition = ""
            product_id = "Windows"
            id_like = "Windows NT"
            version_codename = ""
            registered_owner = ""
            install_date = ""
            system_type = "Client"
            return {
                "System": "Windows",
                "Version": "unknown",
                "Name": "Windows",
                "ID": "windows",
                "ID_Like": "Windows NT",  
                "Version_Codename": "",   
                "Architecture": "unknown",
                "error": str(reg_error)
            }
    
        full_name = product_name
        if edition and edition not in full_name:
            full_name += f" {edition}"
        else:
            full_name = product_name
    
        if architecture == "AMD64":
            arch_display = "x86_64"
        elif architecture == "x86":
            arch_display = "i386"
        else:
            arch_display = architecture
        
        kernel_version = "10" if "10" in product_name else release
    
        return {
            "System": product_id, 
            "Version": build_nb,
            "Name": full_name,
            "ID": product_id.lower().replace(" ", "_"),
            "ID_Like": id_like,  
            "Version_Codename": version_codename, 
            "Architecture": arch_display,
            "Kernel": kernel_version,  
            "Build": build_nb,  
            "Edition": edition,  
            "Type": system_type, 
            "DisplayVersion": display_version,
            "Owner": registered_owner, 
            "InstallDate": install_date 
        }
        
        
    #corriger/ marche
    def get_linux_details(self):
        try: 
            # vias os release file
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release','r') as f:
                    lines = f.readlines()
                os_info = {}
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                
                architecture = platform.machine()
                kernel_version = platform.release()
                try:
                    with open('/etc/hostname', 'r') as f :
                        hostname = f.read().strip()
                except:
                    hostname = platform.node()
                
                try:
                    shell = os.environ.get('SHELL', 'unknows')
                except:
                    shell = 'unknown'
                    
                install_date = ""
                try:
                    install_timestamp = os.path.getctime('/etc/hostname')
                    install_date = datetime.datetime.fromtimestamp(install_timestamp).strftime('%Y-%m-%d')
                except:
                    pass
                    
                
                return {
                    "System": os_info.get("NANE", "Linux"),
                    "Version": os_info.get("VERSION_ID", "unknown"),
                    "Name": os_info.get("PRETTY_NAME", "Unknown Linux"),
                    "ID": os_info.get("ID", "unknown"),
                    "ID_Like": os_info.get("ID_LIKE", ''),
                    "Version_codename": os_info.get("VERSION_CODENAME", ''),
                    "Architecture": architecture,
                    "Kernel": kernel_version,
                    "Build": os_info.get("BUILD_ID", kernel_version),
                    "Edition": os_info.get("VARIANT", ""),
                    "Type": os_info.get("TYPE", ""),
                    "DisplayVersion" : os_info.get("VERSION", ""),
                    "Shell": shell,
                    "Owner": hostname,
                    "InstallDate": ""
                }
            else:
                architecture = platform.machine()
                kernel_version = platform.release()
                hostname = platform.node()
                return {
                    "System": "Linux",
                    "Version": platform.release(),
                    "Name": "Generic Linux",
                    "ID": "linux",
                    "ID_Like": "",
                    "Version_Codename": "",
                    "Architecture": architecture,
                    "Kernel": kernel_version,
                    "Build": kernel_version,
                    "Edition": "",
                    "Type": "Desktop",
                    "DisplayVersion": "",
                    "Owner": hostname,
                    "InstallDate": ""
                }
        except Exception as e:
            return {
                "System": "Linux",
                "Version": "unknown",
                "Name": "Linux",
                "ID": "linux",
                "ID_Like": "",
                "Version_Codename": "",
                "Architecture": "unknown",
                "Kernel": "unknown",
                "Build": "unknown",
                "Edition": "",
                "Type": "Desktop",
                "DisplayVersion": "",
                "Owner": "unknown",
                "InstallDate": "",
                "error": str(e)
            }
            
    
