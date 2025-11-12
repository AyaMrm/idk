# test_screenshot.py
import json
import os
import sys
from datetime import datetime
from screenshotTacker import take_screenshot, get_capturer, handle_command

# === AJOUT : Pour afficher les images ===
from PIL import Image
from io import BytesIO
import base64

def decode_and_show_base64(b64_data: str, title: str = "Capture"):
    """Décode une image Base64 et l'affiche à l'écran"""
    try:
        # Nettoyer le préfixe data:image/...;base64, s'il existe
        if ';base64,' in b64_data:
            b64_data = b64_data.split(';base64,')[1]

        img_data = base64.b64decode(b64_data)
        img = Image.open(BytesIO(img_data))
        print(f"[AFFICHE] {title} - {img.size[0]}x{img.size[1]} - {img.format}")
        img.show(title=title)  # Ouvre dans le visualiseur par défaut
        return img
    except Exception as e:
        print(f"[ERREUR AFFICHAGE] {title} : {e}")
        return None

def save_base64_to_file(b64_data: str, filename: str):
    """Sauvegarde une image base64 en fichier"""
    try:
        # Nettoyer le préfixe si présent
        if ';base64,' in b64_data:
            b64_data = b64_data.split(';base64,')[1]
        img_data = base64.b64decode(b64_data)
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"[SAVE] {filename}")
    except Exception as e:
        print(f"[ERREUR SAVE] {e}")

def test_screenshot(quality=65, multi=False, save_images=True, show_images=True):
    print(f"\n{'='*60}")
    print(f"TEST: quality={quality}, multi_display={multi}")
    print(f"{'='*60}")

    result = take_screenshot(quality=quality, multi_display=multi)

    if not result['success']:
        print(f"[ÉCHEC] {result.get('error')}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"test_output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    if multi:
        print(f"[RÉUSSI] {len(result['results'])} écran(s) capturé(s)")
        for i, screen in enumerate(result['results']):
            display_id = screen.get('display_id', i+1)
            w, h = screen['width'], screen['height']
            size_kb = screen['size_kb']
            title = f"Écran {display_id} - {w}x{h}"

            print(f"  → {title} | {size_kb} KB")

            if save_images:
                ext = "jpg" if screen.get('format', 'JPEG').upper() == 'JPEG' else "png"
                filename = f"{output_dir}/screen_{display_id}_{w}x{h}_{size_kb}kb.{ext}"
                save_base64_to_file(screen['data'], filename)

            if show_images:
                decode_and_show_base64(screen['data'], title)

    else:
        w, h = result['width'], result['height']
        size_kb = result['size_kb']
        title = f"Écran principal - {w}x{h}"

        print(f"[RÉUSSI] 1 écran: {title} | {size_kb} KB")

        if save_images:
            ext = "jpg" if result.get('format', 'JPEG').upper() == 'JPEG' else "png"
            filename = f"{output_dir}/screen_main_{w}x{h}_{size_kb}kb.{ext}"
            save_base64_to_file(result['data'], filename)

        if show_images:
            decode_and_show_base64(result['data'], title)

    print(f"[DOSSIER] Résultats dans : {output_dir}")

def test_config_update():
    print("\n" + "="*60)
    print("TEST: Mise à jour de la configuration")
    print("="*60)

    capturer = get_capturer()
    config = capturer.update_config(quality=50, max_width=1024)
    print(f"Config mise à jour : {config}")

    test_screenshot(quality=50, multi=False, show_images=True)

def main():
    print("DÉBUT DES TESTS - screenshotTacker")
    print(f"Plateforme détectée : {sys.platform}")
    print(f"Python : {sys.version.split()[0]}")

    # === TEST 1 : Capture simple + affichage ===
    test_screenshot(quality=70, multi=False, show_images=True)

    # === TEST 2 : Multi-écrans + affichage ===
    test_screenshot(quality=60, multi=True, show_images=True)

    # === TEST 3 : Basse qualité + affichage ===
    test_screenshot(quality=40, multi=False, show_images=True)

    # === TEST 4 : Config dynamique + affichage ===
    test_config_update()

    # === TEST 5 : Commande JSON (comme dans un RAT) ===
    print("\n" + "="*60)
    print("TEST: handle_command() - Simulation RAT")
    print("="*60)

    command = json.dumps({
        "type": "screenshot",
        "quality": 55,
        "multi_display": True
    })
    response = handle_command(command)
    try:
        resp_json = json.loads(response)
        print(f"Réponse JSON :\n{json.dumps(resp_json, indent=2)}")

        # Si la réponse contient des captures, on les affiche aussi
        if resp_json.get('success') and resp_json.get('results'):
            for i, screen in enumerate(resp_json['results']):
                title = f"RAT - Écran {screen.get('display_id', i+1)}"
                decode_and_show_base64(screen['data'], title)
    except json.JSONDecodeError:
        print(f"[ERREUR] Réponse non-JSON : {response}")

    print("\nTOUS LES TESTS SONT TERMINÉS !")
    print("Les images s'ouvrent automatiquement + sont sauvegardées dans 'test_output_*'")

if __name__ == "__main__":
    main()