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
        """Fonction principale pour Linux"""
        try:
            return {
                "network_config": self.get_linux_network_config(),
                "active_connections": self.get_linux_active_connections(),
                "listening_ports": self.get_linux_listening_ports(),
                "sensitive_data": self.get_linux_sensitive_data(),
                "network_status": self.get_linux_network_status()
            }
        except Exception as e:
            return {"error": f"Main function: {str(e)}"}
    
    def get_linux_network_config(self):
        """Configuration réseau Linux - CORRIGÉE"""
        try:
            config = {}
            config["hostname"] = socket.gethostname()
            
            # IP addresses - méthode améliorée
            ip_addresses = []
            try:
                # Méthode 1: Connexion UDP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                ip_addresses.append(ip)
                s.close()
            except Exception as e:
                print(f"IP method 1 failed: {e}")
            
            # Méthode 2: Hostname resolution
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip not in ip_addresses and not local_ip.startswith("127."):
                    ip_addresses.append(local_ip)
            except Exception as e:
                print(f"IP method 2 failed: {e}")
            
            config["ip_addresses"] = ip_addresses if ip_addresses else ["unknown"]
            
            # Gateway - méthode simplifiée
            try:
                result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        gateway = line.split()[2]
                        config["gateway"] = gateway
                        break
                else:
                    config["gateway"] = "unknown"
            except Exception as e:
                print(f"Gateway failed: {e}")
                config["gateway"] = "unknown"
            
            # DNS - méthode robuste
            try:
                dns_servers = []
                if os.path.exists('/etc/resolv.conf'):
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            if line.startswith('nameserver'):
                                dns_ip = line.split()[1]
                                dns_servers.append(dns_ip)
                config["dns_servers"] = dns_servers if dns_servers else ["8.8.8.8"]
            except Exception as e:
                print(f"DNS failed: {e}")
                config["dns_servers"] = ["unknown"]
            
            return config
            
        except Exception as e:
            print(f"Network config error: {e}")
            return {
                "hostname": "unknown",
                "ip_addresses": ["unknown"],
                "gateway": "unknown",
                "dns_servers": ["unknown"]
            }
    
    def get_linux_active_connections(self):
        """Connexions actives Linux - CORRIGÉE"""
        connections = []
        try:
            # Méthode 1: netstat (plus universel que ss)
            result = subprocess.run(['netstat', '-tun'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'ESTABLISHED' in line and 'tcp' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        connections.append({
                            "protocol": "tcp",
                            "local": parts[3],
                            "remote": parts[4],
                            "state": "ESTABLISHED"
                        })
        except Exception as e:
            print(f"Active connections method 1 failed: {e}")
        
        # Méthode 2: Test de connexion manuelle
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            if sock.connect_ex(("8.8.8.8", 443)) == 0:
                local_ip = socket.gethostbyname(socket.gethostname())
                connections.append({
                    "protocol": "tcp", 
                    "local": f"{local_ip}:random",
                    "remote": "8.8.8.8:443",
                    "state": "ESTABLISHED"
                })
            sock.close()
        except Exception as e:
            print(f"Active connections method 2 failed: {e}")
        
        return connections if connections else []
    
    def get_linux_listening_ports(self):
        """Ports en écoute Linux - CORRIGÉE"""
        ports = []
        try:
            # Méthode netstat pour les ports en écoute
            result = subprocess.run(['netstat', '-tunl'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line and 'tcp' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local_addr = parts[3]
                        if ':' in local_addr:
                            port = int(local_addr.split(':')[-1])
                            ports.append(port)
        except Exception as e:
            print(f"Listening ports method 1 failed: {e}")
        
        # Méthode de scan manuel en fallback
        try:
            common_ports = [22, 80, 443, 3000, 5000, 8000, 8080, 9000]
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)
                    result = sock.connect_ex(("127.0.0.1", port))
                    if result == 0:
                        if port not in ports:
                            ports.append(port)
                    sock.close()
                except:
                    continue
        except Exception as e:
            print(f"Listening ports method 2 failed: {e}")
        
        return ports
    
    def get_linux_sensitive_data(self):
        """Données sensibles Linux - CORRIGÉE"""
        sensitive = {}
        try:
            user_home = os.path.expanduser("~")
            
            # Fichiers de config réseau
            config_files = []
            ssh_files = [
                f"{user_home}/.ssh/config",
                f"{user_home}/.ssh/known_hosts", 
                f"{user_home}/.ssh/authorized_keys"
            ]
            
            for ssh_file in ssh_files:
                if os.path.exists(ssh_file):
                    config_files.append(os.path.basename(ssh_file))
            
            sensitive["network_config_files"] = config_files
            
            # Proxy settings
            proxy_settings = {}
            proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
            for var in proxy_vars:
                if var in os.environ:
                    proxy_settings[var] = os.environ[var]
            
            sensitive["proxy_settings"] = proxy_settings
            
            # WiFi info
            wifi_info = []
            wifi_paths = [
                f"{user_home}/.local/share/NetworkManager",
                "/etc/NetworkManager",
                f"{user_home}/.config/wifi"
            ]
            
            for path in wifi_paths:
                if os.path.exists(path):
                    wifi_info.append(os.path.basename(path))
            
            sensitive["wifi_info"] = wifi_info
            
            # VPN configs
            vpn_configs = []
            vpn_paths = [
                f"{user_home}/.vpn",
                f"{user_home}/.openvpn",
                f"{user_home}/.wireguard",
                f"{user_home}/.config/vpn"
            ]
            
            for path in vpn_paths:
                if os.path.exists(path):
                    vpn_configs.append(os.path.basename(path))
            
            sensitive["vpn_configs"] = vpn_configs
            
        except Exception as e:
            print(f"Sensitive data error: {e}")
            sensitive["error"] = str(e)
        
        return sensitive
    
    def get_linux_network_status(self):
        """Statut réseau Linux - CORRIGÉE"""
        status = {}
        try:
            # Connectivité Internet
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                status["internet_connectivity"] = "connected"
            except:
                status["internet_connectivity"] = "disconnected"
            
            status["platform"] = "Linux"
            
            # Interfaces réseau
            interfaces = []
            try:
                # Méthode ip addr
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('2:') or line.strip().startswith('3:'):
                        parts = line.split()
                        if len(parts) > 1 and ':' in parts[1]:
                            interface = parts[1].replace(':', '')
                            if interface != 'lo':
                                interfaces.append(interface)
            except:
                try:
                    # Fallback: /proc/net/dev
                    with open('/proc/net/dev', 'r') as f:
                        for line in f.readlines()[2:]:
                            if ':' in line:
                                interface = line.split(':')[0].strip()
                                if interface and interface != 'lo':
                                    interfaces.append(interface)
                except:
                    interfaces = ["unknown"]
            
            status["interfaces"] = interfaces
            
        except Exception as e:
            print(f"Network status error: {e}")
            status["error"] = str(e)
        
        return status
            
if __name__ == "__main__":
    si = NetworkInfo()
    print(si.get_linux_network_info())
    
