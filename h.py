# implant/test_simple.py
import socket
import time

print("🔍 Test Simple - Connexion à c2.local...")

while True:
    try:
        ip = socket.gethostbyname("c2.local")
        print(f"✅ c2.local → {ip}")
        
        sock = socket.socket()
        sock.settimeout(5)
        sock.connect((ip, 443))
        print("🎉 CONNECTÉ AU C2 !")
        
        sock.send(b"Hello C2!")
        response = sock.recv(1024)
        print(f"📨 C2 répond: {response.decode()}")
        
        sock.close()
        break
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💤 Nouvelle tentative dans 5s...")
        time.sleep(5)
