import platform
import subprocess
import os

class PrivilgesInfo():
    def __init__(self):
        self.get_privileges = self.get_privileges_info()
        
    def get_privileges_info(self):
        system = platform.system().lower()
        
        if system == 'windows':
            return self.get_windows_privileges()
        elif system == 'linux':
            return self.get_linux_privileges()
        else:
            return self.get_genenric_privileges()
        
    def get_windows_privileges(self):
        try:
            import winreg
            import subprocess
            
            privileges ={
                "Current privileges": self.get_windows_token_privilges(),
                "Escalation methods": self.find_windows_escalation_methods(),
                "System weaknesses": self.find_windows_weaknesses(),
                "Integrity level": self.get_windows_integrity_level()
            }
            return {"Privileges": privileges}
        except Exception as e:
            return {"Privileges": {"Error": str(e)}}
    
    def get_windows_token_privilges(self):
        privileges =[]
        try:
            result = subprocess.run(['whoami', '/priv'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Enabled' in line and line.startswith('Se'):
                        privilege = line.split()[0].strip()
                        privileges.append(privilege)
        except:
            pass
        return privileges if privileges else ["SeChangeNotifyPrivilge"]
    
    def find_windows_escalation_methods(self):
        methods = []
        if self.is_uac_bypass_possible():
            methods.append("uac_bypass")
        if self.has_vulnerable_services():
            methods.append("service_abuse")
        if self.has_writable_scheduled_tasks():
            methods.append("sheduled_task_hijack")
        
        return methods
    
    def find_windows_weaknesses(self):
        weaknesses = []
    
        if self.check_always_install_elevated():
            weaknesses.append("always_install_elevated")
        if self.has_unquoted_service_paths():
            weaknesses.append("unquoted_service_paths")
        if self.check_sticky_keys():
            weaknesses.append("sticky_keys_backdoor")
    
        return weaknesses
    
    def get_windows_integrity_level(self):
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                return "Hight"
            else:
                return "Medium"
        except:
            return "Uknown"
        
    def is_uac_bypass_possible(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
                uac_value = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")[0]
                return uac_value in [0, 2]
        except:
            return False
        
    def has_vulnerable_services(self):
        vulnerable_services =[]
        try:
            result = subprocess.run(['sc', 'query'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_service = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith('SERVICE_NAME:'):
                        current_service = line.split(':')[1].strip()
                    elif current_service and 'WIN32_OWN_PROCESS' in line :
                        perm = subprocess.run(['sc', 'qc'], capture_output=True, text=True, timeout=5)
                        if perm.returncode == 0:
                            service_config = perm.stdout
                            if any(indicator in service_config for indicator in ['INTERACTIVE', 'LocalSystem', 'NULL SESSION']):
                                vulnerable_services.append(current_service)
            return len(vulnerable_services) >0
        except Exception as e:
            return False
    
    def has_writable_scheduled_tasks(self):
        try:
            task_paths = [r'C:\Windows\System32\Tasks', 
                          r'C:\Windows\Tasks', 
                          os.path.join(os.environ.get('ProgramData', ''), 'Microsoft', 'Windows', 'TaskScheduler')
                    ]
            for Tpath in task_paths:
                if os.path.exists(Tpath):
                    try:
                        test = os.path.join(Tpath, 'test.map')
                        with open(test, 'w') as f:
                            f.write('test')
                        os.remove(test)
                    except:
                        continue
            result = subprocess.run(['schtasks', '/query', '/fo', 'LIST'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                tasks = result.stdout.count('TaskName:')
                return tasks > 0
            return False
        except Exception as e:
            return False
    
    def check_always_install_elevated(self):
        try: 
            import winreg 
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Installer")as key:
                lm_value = winreg.QueryValueEx(key, "AlwaysInstallElevated")[0]
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Policies\Microsoft\Windows\Installer") as key:
                cu_value = winreg.QueryValueEx(key, "AlwaysInstallElevated")[0]
                
            return lm_value == 1 and cu_value == 1
        except : 
            return False
        
    def check_sticky_keys(self):
        try:
            result = subprocess.run(['reg', 'query', 
            'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Accessibility', 
            '/v', 'Configuration'], capture_output=True, text=True)
            
            return result.returncode == 0
        except:
            return False
        
    def has_unquoted_service_paths(self):
        try:
            import winreg 
            unquoted_services = []
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services") as services_key:
                i =0
                while True:
                    try:
                        service_name = winreg.EnumKey(services_key, i)
                        i += 1
                        try:
                             with winreg.OpenKey(services_key, service_name) as service_key:
                                try:
                                    image_path = winreg.QueryValueEx(service_key, "ImagePath")[0]
                                    
                                    if (isinstance(image_path, str) and ' ' in image_path and not image_path.startswith('"') and'.exe' in image_path.lower()):
                                        if not image_path.startswith('\\SystemRoot') and 'system32\\drivers' not in image_path.lower():
                                            unquoted_services.append(service_name)
                                except FileNotFoundError:
                                    pass
                        except:
                            continue
                    except OSError:
                        break
                return len(unquoted_services) > 0
        except Exception as e :
            return False
        
    # maintanant je passe au cotee linux 
    def get_linux_privileges(self):
        try:
            import grp 
            privilges = {
                "Current privileges": self.get_linux_capabilities(),
                "Escalation methods": self.find_linux_escalation_methods(),
                "System weaknesses": self.find_linux_weaknesses(),
                "Integrity level": "root" if os.geteuid() ==0 else "user"
            }
            return {"Privileges": privilges}
        except Exception as e :
            return { " Privileges": str(e)}
            
    
    def get_linux_capabilities(self):
        """Récupère les capabilities du processus sans root"""
        try:
            # Méthode 1: Lire depuis /proc/self/status
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('Cap'):
                        return line.strip()
            return "No capabilities found"
        except:
            try:
                # Méthode 2: Utiliser capsh si disponible
                result = subprocess.run(
                    ['capsh', '--print'], 
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Current' in line and '=' in line:
                            return line.split('=')[1].strip()
                return "Unknown capabilities"
            except:
                return "Unable to determine capabilities"
    
    def find_linux_escalation_methods(self):
        """Trouve les méthodes d'escalade de privilèges sans root"""
        methods = []
        
        try:
            # 1. Vérifier SUID dans les dossiers accessibles
            accessible_dirs = [
                os.path.expanduser("~"),
                "/tmp", "/var/tmp",
                "/opt", "/usr/local/bin",
                "/home"
            ]
            
            for directory in accessible_dirs:
                if os.path.exists(directory):
                    result = subprocess.run(
                        ['find', directory, '-perm', '-4000', '-type', 'f', '2>/dev/null'],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.stdout.strip():
                        methods.append("suid_binaries_found")
                        break
        except:
            pass
        
        # 2. Vérifier sudo sans mot de passe
        try:
            result = subprocess.run(
                ['sudo', '-n', 'whoami'], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "root" in result.stdout:
                methods.append("passwordless_sudo")
        except:
            pass
        
        # 3. Vérifier les capabilities dangereuses
        try:
            caps = self.get_linux_capabilities()
            dangerous_caps = ["cap_sys_admin", "cap_sys_ptrace", "cap_sys_module"]
            for cap in dangerous_caps:
                if cap in str(caps):
                    methods.append(f"dangerous_capability_{cap}")
        except:
            pass
        
        # 4. Vérifier l'appartenance à des groupes privilégiés
        try:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            privileged_groups = ["docker", "lxd", "sudo", "wheel", "adm"]
            for group in privileged_groups:
                if group in result.stdout:
                    methods.append(f"privileged_group_{group}")
        except:
            pass
        
        return methods
    
    def find_linux_weaknesses(self):
        """Trouve les faiblesses du système sans root"""
        weaknesses = []
        
        try:
            # A) Fichiers configurables par l'utilisateur
            user_configs = [
                os.path.expanduser("~/.bashrc"),
                os.path.expanduser("~/.bash_profile"), 
                os.path.expanduser("~/.profile"),
                os.path.expanduser("~/.zshrc"),
                os.path.expanduser("~/.ssh/authorized_keys"),
                os.path.expanduser("~/.ssh/config"),
            ]
            
            for config in user_configs:
                if os.path.exists(config):
                    if os.access(config, os.W_OK):
                        weaknesses.append(f"writable_{os.path.basename(config)}")
            
            # B) Variables d'environnement dangereuses
            dangerous_env = ["LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH"]
            for env_var in dangerous_env:
                if env_var in os.environ:
                    weaknesses.append(f"dangerous_env_{env_var}")
            
            # C) Sudo sans mot de passe pour commandes spécifiques
            try:
                result = subprocess.run(
                    ['sudo', '-l'], 
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    if "NOPASSWD" in result.stdout:
                        weaknesses.append("sudo_nopasswd")
                    # Vérifier les commandes spécifiques
                    for line in result.stdout.split('\n'):
                        if any(cmd in line for cmd in ['/bin/bash', '/bin/sh', 'python', 'perl']):
                            if 'NOPASSWD' in line:
                                weaknesses.append(f"sudo_{cmd}_nopasswd")
            except:
                pass
            
            # D) Appartenance au groupe docker
            try:
                result = subprocess.run(['id', '-nG'], capture_output=True, text=True)
                if "docker" in result.stdout:
                    weaknesses.append("docker_group_access")
            except:
                pass
            
            # E) Scripts exécutables par tous
            try:
                home_dir = os.path.expanduser("~")
                result = subprocess.run(
                    ['find', home_dir, '-type', 'f', '-perm', '-o=x', '-name', '*.sh', '2>/dev/null'],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout.strip():
                    weaknesses.append("world_executable_scripts")
            except:
                pass
            
            # F) Fichiers temporaires accessibles
            try:
                test_file = "/tmp/security_test"
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                weaknesses.append("writable_tmp")
            except:
                pass
            
            return weaknesses
            
        except Exception as e:
            return [f"scan_error: {str(e)}"]
        
        
        
if __name__ == "__main__":
    si = PrivilgesInfo()
    print(si.get_privileges_info())  
                                                       
