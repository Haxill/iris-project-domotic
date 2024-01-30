'''
########################################################################################################################################
# Created by : HAXILL                                                                                                                  #
# Engine     : tkinter, colorama, requests, importlib, miio, datetime, scapy, time, os.                                                #
# Date       : 22/02/2023                                                                                                              #
# Version    : 30/01/2024                                                                                                              #
# OS         : Windows 10                                                                                                              #
# Python     : Python 3.9.13 (tags/v3.9.13:6de2ca5, May 17 2022, 16:36:42)                                                             #
# Langue     : French                                                                                                                  #
# Script     : Script de programmation de l'aspirateur robot Xiaomi : Mi Robot Vacuum-Mop 2 Pro. Affichant tous les détails            #
#              importants dans une fenêtre. Il vérifie votre présence, grâce à votre smartphone, et ne lance l'aspirateur que lors de  #
#              votre absence. Si vous rentrez pendant son passage, il retourne à la base immédiatement.                                #
#              Les données sont récupérées par Iris-GPT4.py pour vous dire si l'aspirateur a été passé en votre absence.               #
########################################################################################################################################
'''

import tkinter as tk
from colorama import init, Fore, Style
import requests
import importlib
import miio
from miio import RoidmiVacuumMiot
import datetime
from scapy.all import ARP, Ether, srp
import time
import os


''' TEST DE CONNEXION '''
# Fonction de vérification de connexion internet
def test_connexion():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

# Test de la connexion et arrêt du script en cas d'échec
if test_connexion():
    print(f"{Fore.GREEN}Internet = OK{Style.RESET_ALL}\n")
    time.sleep(2)
else:
    print(f"\n{Fore.RED}Erreur de connexion Internet.\nVérifiez votre connexion.{Style.RESET_ALL}\n")
    quit()
''''''

''' TELECHARGEMENT DES MODULES ET BIBLIOTHEQUES NECESSAIRES '''
os.system("cls")
print("\nVérification des prérequis...\n")

# Liste des modules nécessaires
required_modules = ['tk', 'datetime', 'os', 'python-miio', 'requests', 'colorama', 'importlib', 'scapy']

# Fonction de check des modules nécessaires au fonctionnement du script
def check_and_install_module(module_name):
    try:
        # Tentative d'import du module
        importlib.import_module(module_name)
        print(f"{Fore.GREEN}{module_name} est déjà installé.{Style.RESET_ALL}")
    except ImportError:
        # Installation du module avec pip
        print(f"{Fore.YELLOW}Installation de {module_name}...{Style.RESET_ALL}")
        os.system(f"pip install {module_name}")

# Vérification et installation des modules nécessaires
for module in required_modules:
    check_and_install_module(module)

# Initialisation de colorama
init()
''''''

# Variable partagée (pour écriture dans un fichier car l'IPC fige le script)
aspirateurVar = 0

# Adresse IP et token de mon aspirateur robot Xiaomi
ip = "192.168.0.1"
token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Mon téléphone Xiaomi
telephone = "192.168.0.2"
# Mon adresse mac du téléphone Xiaomi
adresseMac = "AB:CD:EF:AB:CD:EF"

# Initialisation du booléen de passage de l'aspirateur ce jour
aspiAujourdhui = False
# Initialisation du booléen de détection de présence
isconnected = False
# Initialisation du booléen indiquant si le robot fait le ménage ou non
nettoyage = False

# Heure de réinitialisation (minuit = 0:0)
reinitH = 0  # Heure
reinitM = 0  # Minutes

# Connexion à l'aspirateur robot Xiaomi
aspirobot = RoidmiVacuumMiot(ip, token)

# Fonction de démarrage de l'aspirateur ou de retour au dock
def aspiStartRetour():
    if not isconnected:
        log_text.set("Démarrage du robot.")
        aspirobot.start()
    else:
        aspirobot.home()

def update_status():
    global aspiAujourdhui  # Utilisation de la variable globale
    # Obtention de la date actuelle
    now = datetime.datetime.now()
    # Extraction de la date et l'heure pour chatGPT
    year = now.year
    mois_list = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    mois = mois_list[now.month]
    jour = now.day
    heure = now.hour
    minutes = now.minute

    if heure == reinitH and minutes == reinitM:
        aspiAujourdhui = False  # On réinitialise si l'aspirateur est déjà passé

    # Vérification de ma présence à la maison
    # Création d'une requête ARP
    arp = ARP(pdst=telephone)
    # Création d'une trame Ethernet avec l'@MAC du téléphone
    ether = Ether(dst=adresseMac)
    # Fusion de la requête et de la trame
    packet = ether/arp
    # Envoie de la requête ARP et récupération des réponses
    result = srp(packet, timeout=2, verbose=0)[0]
    result = srp(packet, timeout=2, verbose=0)[0]

    # Récupération des informations de l'aspirateur et traitement des erreurs
    try:
        status = aspirobot.status()
    except miio.exceptions.RecoverableError:
        status = aspirobot.status()
    except miio.exceptions.DeviceException:
        status = aspirobot.status()

    try:
        # Obtention du niveau de batterie
        battery_level = status.battery
        # Détermination de l'action en cours du robot
        is_on = status.is_on
        if not is_on:
            is_on = "Nettoyage en cours..."  # False
            nettoyage = True
        else:
            if battery_level < 100:
                is_on = "En charge..."  # True
            else:
                is_on = "En veille"
            nettoyage = False
    except Exception as e:
        log_text.set("Une erreur s'est produite : " + str(e))
        return

    # Analyse de la réponse à la requête
    if len(result) > 0:
        isconnected = True  # Présent
    else:
        isconnected = False  # Absent

    if not isconnected:  # Pas de présence détectée
        current_time = datetime.datetime.now()
        if heure == 13 and minutes == 30 and not aspiAujourdhui:   # 1er essai à une heure donnée (13h30)
            aspiStartRetour()
            aspiAujourdhui = True
        elif heure == 15 and minutes == 30 and not aspiAujourdhui: # 2eme essai si l'aspirateur n'a pas démarré au premier horaire (15h30)
            aspiStartRetour()
            aspiAujourdhui = True
        else:
            log_text.set("\n\n"
                         "   - Etat : {}\n"
                         "   - Niveau de batterie : {}%\n".format(is_on, battery_level))
            if nettoyage:
                log_text.set(log_text.get() + "\nPersonne dans les parages. Passage de l'aspirateur en cours...\n\n")
            else:
                log_text.set(log_text.get() + "\nPersonne dans les parages.")
    else:  # Présence détectée
        if nettoyage:
            aspiStartRetour()
            log_text.set("\n\n"
                         "   - Etat : Retour au socle en cours...\n"
                         "   - Niveau de batterie : {}%\n".format(battery_level))
        else:
            log_text.set("\n\n"
                         "   - Etat : {}\n"
                         "   - Niveau de batterie : {}%\n".format(is_on, battery_level))
        log_text.set(log_text.get() + "\nPrésence détectée. Vous êtes à la maison.")
    if aspiAujourdhui:
        log_text.set(log_text.get() + "\nL'aspirateur est déjà passé pour aujourd'hui.\n")
        aspirateurVar = 1
        # Écriture de la variable partagée dans le fichier 'aspivarfile.txt'
        with open('aspivarfile.txt', 'w') as file:
            file.write(str(aspirateurVar))
#    elif aspiAujourdhui and nettoyage:
    elif nettoyage:
        log_text.set(log_text.get() + "\nL'aspirateur est en train d'être passé.\n")
        aspirateurVar = 3
        # Écriture de la variable partagée dans le fichier 'aspivarfile.txt'
        with open('aspivarfile.txt', 'w') as file:
            file.write(str(aspirateurVar))
    else:
        log_text.set(log_text.get() + "\nL'aspirateur n'a pas encore été passé aujourd'hui.\n")
        aspirateurVar = 0
        # Écriture de la variable partagée dans le fichier 'aspivarfile.txt'
        with open('aspivarfile.txt', 'w') as file:
            file.write(str(aspirateurVar))

    # Temporisation de l'update des status (30 secondes)
    root.after(30000, update_status)

# Création de l'objet fenêtre
root = tk.Tk()
root.title("Script de mon aspirateur")
root.geometry("400x300")

# Style
root.configure(bg="#F0F0F0")
font_title = ("Arial", 14, "bold")
font_text = ("Arial", 12)

# Cadre principal
main_frame = tk.Frame(root, bg="#F0F0F0")
main_frame.pack(pady=20)

# Titre
title_label = tk.Label(main_frame, text="Status du Robot Aspirateur", font=font_title, bg="#F0F0F0")
title_label.pack()

# Cadre pour le statut
status_frame = tk.Frame(main_frame, bg="#F0F0F0", padx=20, pady=10)
status_frame.pack()

# Statut du robot
log_text = tk.StringVar() # Déclaration de la variable log_text
status_label = tk.Label(status_frame, textvariable=log_text, font=font_text, justify="left", bg="#F0F0F0")
status_label.pack()

# Mise à jour du statut
update_status()

root.mainloop()
