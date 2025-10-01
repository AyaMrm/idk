# Server/universal_server.py
import socket
import threading
import time

class UniversalServer:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        
    def start(self):
        print("🎮 SERVEUR UNIVERSEL - PRÊT POUR TOUTES LES MÉTHODES")
        print(f"📡 Écoute sur {self.host}:{self.port}")
        print("🌐 Supporte: IP directe, mDNS, DNS local, Domaine Internet, Scan réseau")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(10)
        
        while True:
            client, addr = server.accept()
            print(f"\n🎯 NOUVELLE CONNEXION: {addr}")
            
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()
    
    def handle_client(self, client, addr):
        try:
            # Recevoir message
            message = client.recv(1024).decode()
            print(f"📨 {addr} dit: {message}")
            
            # Répondre
            welcome = f"BIENVENUE! Vous êtes connecté via {addr}"
            client.send(welcome.encode())
            
            # Envoyer commandes de test
            for i in range(5):
                cmd = f"test_command_{i+1}"
                client.send(cmd.encode())
                print(f"📤 Envoyé: {cmd}")
                
                # Recevoir réponse
                response = client.recv(1024).decode()
                print(f"📥 Réponse: {response}")
                
                time.sleep(2)
                
        except Exception as e:
            print(f"💥 Erreur: {e}")
        finally:
            client.close()
            print(f"🔌 {addr} déconnecté")

if __name__ == "__main__":
    UniversalServer().start()
