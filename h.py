# Server/server.py
import socket
import threading
import time
from cryptography.fernet import Fernet
import base64

class PublicC2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        
        # 🔐 CORRECTION : Clé correctement formatée
        key = b"malware_lab_secure_key_2024_32bytes!!"
        # Padding pour faire exactement 32 bytes
        key = key.ljust(32)[:32]
        # Encodage base64 URL-safe
        self.encryption_key = base64.urlsafe_b64encode(key)
        self.crypto = Fernet(self.encryption_key)
        
        print(f"🔑 Clé de chiffrement: {self.encryption_key}")
        
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
            print(f"📨 Message chiffré reçu de {addr}")
            
            message = self.crypto.decrypt(encrypted_msg).decode()
            print(f"📖 Message déchiffré: {message}")
            
            # Répondre
            welcome_msg = "BIENVENUE sur C2 Internet!"
            encrypted_welcome = self.crypto.encrypt(welcome_msg.encode())
            client.send(encrypted_welcome)
            print("📤 Message de bienvenue envoyé")
            
            # Envoyer quelques commandes de test
            for i in range(3):
                cmd = f"Commande de test #{i+1}"
                encrypted_cmd = self.crypto.encrypt(cmd.encode())
                client.send(encrypted_cmd)
                print(f"📤 Commande envoyée: {cmd}")
                
                # Attendre la réponse
                try:
                    encrypted_response = client.recv(4096)
                    response = self.crypto.decrypt(encrypted_response).decode()
                    print(f"📥 Réponse du client: {response}")
                except:
                    print("⏰ Timeout réponse")
                
                time.sleep(2)
                
        except Exception as e:
            print(f"💥 Erreur avec {addr}: {e}")
        finally:
            client.close()
            print(f"🔌 {addr} déconnecté")

if __name__ == "__main__":
    PublicC2Server().start()
