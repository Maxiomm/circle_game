import pyautogui
import pytesseract
from PIL import Image
from os import remove
import threading
import math
import random
import logging


# Configuration globale
# Chemin vers l'exécutable Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Configuration du logging
logging.basicConfig(filename='circle_drawing_log.log', filemode='w', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Spécifier les coordonnées de la zone à capturer
coordonnees_zone_screenshot = (714, 334, 330, 218)  # Exemple : (x, y, largeur, hauteur)

# Spécifier le chemin pour le fichier .txt
chemin_txt = r"D:\Projetsyt\02_Circle\captures\resultat.txt"

# Spécifier la limite sur le rayon
min_radius = 130
max_radius = 640

# Variable globale pour indiquer si le script doit être arrêté
stop_script = False

# Initialisation du précédent score et du précédent rayon
best_score = 0
best_radius = 0

# Direction aléatoire pour l'ajustement au début du script
if random.randint(0, 1) == 0:
    adjustment_factor = 0.9
else:
    adjustment_factor = 1.1



def draw_circle(center_x, center_y, radius):
    global stop_script

    logging.info(f'Dessin du cercle commencé - Rayon: {radius}')

    # Déplacer la souris vers le point de départ
    pyautogui.moveTo(center_x + radius, center_y)

    # Presser le bouton gauche de la souris
    pyautogui.mouseDown()

    # Dessiner le cercle en utilisant des coordonnées polaires
    for angle in range(0, 360, 10):  # Dessiner tous les 10 degrés pour une meilleure résolution
        if stop_script:
            break  # Sortir de la boucle si stop_script est True

        # Convertir l'angle en radians
        radians_angle = math.radians(angle)

        # Calculer les coordonnées polaires
        x = center_x + int(radius * math.cos(radians_angle))
        y = center_y + int(radius * math.sin(radians_angle))

        # Déplacer la souris vers les nouvelles coordonnées
        pyautogui.moveTo(x, y)

    # Relâcher le bouton gauche de la souris
    pyautogui.mouseUp()



def lire_nombre(chemin_txt):
    # Capture d'écran de la zone spécifiée
    x, y, largeur, hauteur = coordonnees_zone_screenshot
    capture = pyautogui.screenshot(region=(x, y, largeur, hauteur))

    # Enregistrement temporaire de la capture d'écran
    chemin_image = r"D:\Projetsyt\02_Circle\captures\capture.png"
    capture.save(chemin_image)

    # Utilisation de Tesseract OCR pour lire le texte
    texte = pytesseract.image_to_string(Image.open(chemin_image), config="--psm 3")

    # Filtrer uniquement les chiffres du texte
    texte_filtrer = ''.join(c for c in texte if c.isdigit() or c == '.')

    print("\n\n" + texte_filtrer + "\n\n")

    # Convertir le texte en nombre (si possible)
    try:
        nombre_essai = float(texte_filtrer)

        logging.info(f'Score : {nombre_essai}')

        # Écrire le texte dans un fichier .txt
        with open(chemin_txt, 'w') as fichier_txt:
            fichier_txt.write(str(nombre_essai))
            
        return nombre_essai
    
    except ValueError:
        logging.warning('Le score n\'a pas pu être lu correctement.')

        with open(chemin_txt, 'w') as fichier_txt:
            fichier_txt.write("XX.X")

        return None
    
    finally:
        # Supprime les fichiers temporaires
        remove(chemin_image)

    

def adjust_parameters(radius, score, change_ratio = 1.0):
    if score is None:
        # Si le score n'a pas pu être lu, essayez avec un autre rayon aléatoire
        return random.uniform(min_radius, max_radius)

    if score >= best_score:
        # Le score s'est amélioré, gardons cette direction
        change_ratio = 1.0 # Reset du ratio de changement
        new_radius = clamp(radius * adjustment_factor)
        return new_radius
    else:
        # Le score ne s'est pas amélioré, changeons de direction
        change_ratio += 0.05 # Pour éviter d'être bloqué entre 2 rayon lorsque le best_score n'est pas changé
        new_radius = clamp(radius * change_direction_adjustment_factor() * change_ratio)
        return new_radius



def change_direction_adjustment_factor():
    global adjustment_factor
    
    if adjustment_factor == 1.1:
        adjustment_factor = 0.9
        return adjustment_factor
    else:
        adjustment_factor = 1.1
        return adjustment_factor



def clamp(radius): 
    if radius < min_radius: 
        return min_radius
    elif radius > max_radius: 
        return max_radius
    else: 
        return radius 



def input_listener():
    global stop_script

    input("Appuyez sur Entrée pour arrêter le script...\n\n")
    stop_script = True
    logging.info('Arrêt demandé par l\'utilisateur.')



if __name__ == "__main__":
    # Initialisation des paramètres du cercle
    center_x = int(input("Entrez la coordonnée x du centre : "))
    center_y = int(input("Entrez la coordonnée y du centre : "))
    radius = random.uniform(min_radius, max_radius)

    # Démarrage du thread pour écouter l'entrée utilisateur
    thread = threading.Thread(target=input_listener)
    thread.start()

    while not stop_script:
        # Dessiner le cercle
        draw_circle(center_x, center_y, radius)

        # Récupérer et analyser le score
        score = lire_nombre(chemin_txt)

        if score == 99.9:
            print("Cercle parfait avec un radius de " + str(radius))
            stop_script = True  # Définir stop_script à True pour arrêter la boucle
            logging.info('Cercle parfait !')

        elif score >= best_score:
            best_score = score
            best_radius = radius
            logging.info('Nouveau best radius !')

            # Ajuster le rayon du cercle pour le prochain essai
            radius = adjust_parameters(radius, score)
            
        else:
            # Ajuster le rayon du cercle pour le prochain essai
            radius = adjust_parameters(best_radius, score)

    # Attendre que le thread d'écoute de l'entrée se termine
    thread.join()