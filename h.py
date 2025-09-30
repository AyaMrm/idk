# c2_server/server.py
import socket

print("🚀 Serveur C2 Démarré!")
print("📡 J'écoute sur le port 443...")

# Créer le socket serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 443))  # Écoute sur TOUTES les interfaces
server.listen(5)

print("✅ Serveur prêt! En attente de connexions Windows...")

while True:
    # Attendre qu'un client se connecte
    client, addr = server.accept()
    print(f"🎯 NOUVELLE CONNEXION de: {addr}")
    
    # Envoyer un message de bienvenue
    client.send(b"Bienvenue! Je suis le C2 Kali.")
    print("📤 Message de bienvenue envoye")
    
    # Recevoir le message du beacon
    message = client.recv(1024)
    print(f"📨 Beacon dit: {message.decode()}")
    
    # Répondre
    client.send(b"Commande: get_system_info")
    
    # Fermer la connexion pour ce test
    client.close()
    print("🔌 Connexion fermee\n")
