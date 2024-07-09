import math
import pyautogui
import threading

# Variable globale pour indiquer si le script doit être arrêté
stop_script = False

def draw_circle(center_x, center_y, radius):
    global stop_script

    # Déplacer la souris vers le point de départ
    pyautogui.moveTo(center_x + radius, center_y)

    # Presser le bouton gauche de la souris
    pyautogui.mouseDown()

    # Dessiner le cercle en utilisant des coordonnées polaires
    for angle in range(0, 360, 10):  # Dessiner tous les x degrés pour une meilleure résolution
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

def input_listener():
    global stop_script
    input("Appuyez sur Entrée pour arrêter le script...")
    stop_script = True

if __name__ == "__main__":
    # Coordonnées du centre et rayon du cercle
    center_x = int(input("Entrez la coordonnée x du centre : "))
    center_y = int(input("Entrez la coordonnée y du centre : "))
    radius = int(input("Entrez le rayon du cercle : "))

    # Démarrer le thread pour écouter l'entrée utilisateur en parallèle
    thread = threading.Thread(target=input_listener)
    thread.start()

    # Dessiner le cercle
    draw_circle(center_x, center_y, radius)

    # Attendre que le thread d'écoute de l'entrée se termine
    thread.join()
