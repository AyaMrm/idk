import socket
import subprocess
import os
import platform
import json

class NetworkInfo():
    def __init__(self):
        self.get_network_info = self.get_network_info()
        
    def get_network_info(self):
        system = platform.system().lower()
        
        if system == 'windows':
            return self.get_windows_network_info()
        elif system == 'linux':
            return "heyself.get_linux_network_info()"
        else :
            return "hey self.get_generic_network_info()"
        
    def get_linux_network_info(self):
        return {
            "network_config": self.get_linux_network_config(),
            "active_connections": self.get_linux_active_connections(),
            "listening_ports": self.get_linux_listening_ports(),
            "sensitive_data": self.get_linux_sensitive_data(),
            "network_status": self.get_linux_network_status()
        }
        
    def get_linux_network_config(self):
        config = {}
        try:
            config["hostname"] = socket.gethostbyname()
            
            #nkherjou el ip
            ip_adrs = []
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_adrs.append(s.getsockname()[0])
                s.close()
            except:
                pass
            config["ip_addresses"] = ip_adrs
            
            #gateway
            try:
                with open('/proc/net/route', 'r') as f:
                    for line in f.readline()[1:]:
                        parts = line.split()
                        if len(parts) > 2 and parts[1] == '00000000':
                            gateway_hex = parts[2]
                            gateway = '.'.join(str(int(gateway_hex[i:i+2], 16)) for i in range(6, -1, -2))
                            config["gateway"] = gateway
                            break
            except:
                config["gateway"] = "unknown" 
                
            #dns
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    dns_servers = []
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
                    config["dns_servers"] = dns_servers
            except:
                config["dns_servers"] = ["unknown"]
            
        except Exception as e:
            config["error"] = str(e)
            
    def get_linux_active_connections(self):
        connections =[]
        try:
            result = subprocess.run(['ss', '-tunp'], capture_output=True, text=True)
            for line in result.stdout.split('\n')[1:]:
                if 'ESTAB' in line:
                    parts = line.split()
                    if len(parts) >=6 :
                        connections.append({
                            "protocol": "tcp",
                            "local": parts[4],
                            "remote": parts[5],
                            "state": "ESTABLISHED"
                        })
        except :
            try:
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex(("8.8.8.8", 443)) == 0 :
                    connections.append({
                        "protocol": "tcp",
                        "local": f"{socket.gethostbyname(socket.gethostname())}:random",
                        "remote": "8.8.8.8:443",
                        "state": "ESTABLISHED"
                    })
                    sock.close()
            except:
                pass
            
    def get_linux_listening_ports(self):
        ports =[]
        try:
            for port in [22, 80, 443, 3000, 5000, 8000, 8080, 9000]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    if sock.connect_ex(("127.0.0.1", port)) == 0:
                        ports.append(port)
                    sock.close()
                except :
                    pass
        except :
            pass
        return ports 
    
    def get_linux_sensitive_data(self):
        sensitive = {}
        
        try:
            user_home = os.path.expanduser("~")
            
            config_files = []
            ssh_files = [f"{user_home}/.ssh/config", f"{user_home}/.ssh/known_hosts"]
            for f in ssh_files:
                if os.path.exists(f):
                    config_files.append(os.path.basename(f))
                    sensitive["network_config_files"] = config_files
            
            proxy_settings = {}
            for var in ["HTTP_PROXY", "HTTPS_PROXY"]:
                if var in os.environ:
                    proxy_settings[var] = os.environ[var]
                    sensitive["proxy_settings"] = proxy_settings
                    
            wifi_info = []
            if os.path.exists(f"{user_home}/.local/share/NetworkManager"):
                wifi_info.append("networkmanager_configs")
            sensitive["wifi_info"] = wifi_info
            
            vpn_configs = []
            vpn_paths = [f"{user_home}/.vpn", f"{user_home}/.openvpn"]
            for path in vpn_paths:
                if os.path.exists(path):
                    vpn_configs.append(os.path.basename(path))
            sensitive["vpn_configs"] = vpn_configs
        except Exception as e:
            sensitive["error"] = str(e)
        
        return sensitive
    
    def get_linux_network_status(self):
        status ={}
        # la conectivite l'intenet
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            status["internet_connectivity"] = "connected"
        except:
            status["internet_connectivity"] = "disconnected"
            
        status["platform"] = "Linux"
        
        #intefeces
        interfaces = []
        try:
            with open('/proc/net/dev', 'r') as f:
                for line in f.readlines()[2:]:
                    if ':' in line:
                        interface = line.split(':')[0].strip()
                        if interface and interface != 'lo':
                            interfaces.append(interface)
        except :
            pass
        
        status["interfaces"] = interfaces
        
        return status
    
    
    
    
if __name__ == "__main__":
    si = NetworkInfo()
    print(si.get_network_info())  
                                    
