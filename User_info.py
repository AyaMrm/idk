import platform
import getpass
import os

class UserInfo:
    def __init__(self):
        self.detailed_user_data = self.get_user_data()
    
    def get_user_data(self):
        system = platform.system().lower()
        
        base_info = {
            "Username": getpass.getuser(),
            "Privilege level": self.get_privilege_level(system),
            "Home directory": os.path.expanduser('~')
        }
        
        if system == 'windows':
            base_info.update(self.get_windows_specific_data())
        elif system == 'linux':
            base_info.update(self.get_linux_specific_data())
            
        return {"User": base_info}
    
    def get_privilege_level(self, system):
        if system == 'windows':
            try:
                import ctypes
                return "Admin" if ctypes.windll.shell32.IsUserAnAdmin() else "User"
            except :
                return "Unknown"
        else:
            if os.geteuid() == 0:
                return "root"
            else:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['sudo', '-l'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return "Sudo User" if result.returncode==0 else "User"
                except:
                    return "User"
                
    def get_windows_specific_data(self):
        data = {}
        try:
            import winreg
            import ctypes
            from ctypes import wintypes
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
                    uac_value = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")
                    data["uac_level"] = uac_value[0] if isinstance(uac_value, tuple) else uac_value
            except:
                data["uac_level"] ="Unknown"
            
            session_type = "local"
            if os.environ.get('SESSIONNAME', '').startswith('RDP'):
                session_type = "rdp"
            elif 'SSH_CONNECTION' in os.environ:
                session_type = "ssh"
            data["session_type"] = session_type
            
            data["domain"] = os.environ.get('USERDOMAIN', 'WORKGROUP')
            data["domain_joined"] = self.is_windows_domain_joined()
            
            data["integrity_level"] = self.get_windows_integrity_level()
            data["has_debug_privilege"] = self.has_debug_privilege()
        except Exception as e:
            data["error"] = str(e)
        return data
    
    def get_linux_specific_data(self):
        data = {}
        try:
            import pwd
            import grp
            import subprocess
            
            user_info = pwd.getpwnam(getpass.getuser())
            data["uid"] = user_info.pw_uid
            data["gid"] = user_info.pw_gid
            data["shell"] = user_info.pw_shell
            
            groups =[]
            for group in grp.getgrall():
                if getpass.getuser() in group.gr_mem:
                    groups.append(group.gr_mem)
            data["groups"] = groups
            
            data["capabilities"] = self.get_linux_capabilities()
            data["selinux_enabled"] = self.is_selinux_enabled()
            data["apparmor_enabled"] = self.is_apparmor_enabled()
            data["is_container"] = self.is_linux_container()
        except Exception as e:
            data["error"] = str(e)
        return data
    
    def is_windows_domain_joined(self):
        try:
            import subprocess
            result = subprocess.run(
                ['systeminfo'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "Domain:" in result.stdout and "WORKGROUP" not in result.stdout
        except:
            return False
        
    def get_windows_integrity_level(self):
        try:
            import ctypes
            from ctypes import wintypes
            
            PROCESS_QUERY_INFORMATION = 0x0400
            hProcess = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION, False, ctypes.windll.kernel32.GetCurrentProcessId()
            )
            if hProcess:
                try:
                    TokenIntegrityLevel = 0x19
                    token_handle = wintypes.HANDLE()
                    
                    if ctypes.windll.advapi32.OpenProcessToken(
                        hProcess,
                        wintypes.DWORD(0x0008),
                        ctypes.byref(token_handle)
                    ):
                        return "meduim"
                finally:
                    ctypes.windll.kernel32.CloseHandle(hProcess)
        except:
               pass
        return "Unknown"
    
    def has_debug_privilege(self):
        try:
            import ctypes
            from ctypes import wintypes
            
            SE_DEBUG_NAME = "SeDebugPrivilege"
            
            class LUID(ctypes.Structure):
                _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)] 
                
            return False
        except:
            return False
    
    def get_linux_capabilities(self):
        try:
            import subprocess
            result = subprocess.run(
                ['capsh', '--print'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return [line for line in result.stdout.split('\n') if 'Current' in line]
        except:
            pass
        return []
    
    def is_selinux_enabled(self):
        try:
            import subprocess
            result = subprocess.run(
                ['sestatus'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "enabled" in result.stdout
        except:
            return False
        
    def is_apparmor_enabled(self):
        try:
            import subprocess
            result = subprocess.run(
                ['aa-status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def is_linux_container(self):
        checks = [
            './dockerenv',
            '/run/.containerenv',
            '/proc/1/cgroup'
        ]
        for check in checks:
            if os.path.exists(check):
                if check == '/proc/1/cgroup':
                    try:
                        with open('/proc/1/cgroup', 'r') as f :
                            content = f.read()
                            if 'docker' in content or 'kubepods' in content:
                                return True
                    except:
                        pass
                else:
                    return True
        return False
    
    
if __name__ == "__main__":
    si = UserInfo()
    print(si.detailed_user_data)            