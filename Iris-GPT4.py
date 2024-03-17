'''
########################################################################################################################################
# Created by : HAXILL                                                                                                                  #
# Engine     : openai, sqlite3, gTTS, pygame, datetime, speech_recognition, os, miio, Yeelight, requests, zipfile, feedparser, bs4,    #
#              colorama, langdetect, mtranslate.                                                                                       #
# Date       : 18/02/2023                                                                                                              #
# Version    : 28/01/2024                                                                                                              #
# OS         : Windows 10 - Windows 11                                                                                                 #
# Python     : Python 3.9.13 (tags/v3.9.13:6de2ca5, May 17 2022, 16:36:42)                                                             #
# Langue     : French                                                                                                                  #
# Script     : Projet d'IA domotique configurable, contrôlable vocalement et répondant vocalement, permettant de gérer l'éclairage,    #
#              le robot aspirateur XIAOMI (avec variable partagée via un script qui détermine les heures de passage), faire un         #
#              speedtest de connexion, lisant et traduisant les nouvelles actuelles de n'importe quel flux RSS en n'importe qu'elle    #
#              langue. Et avec laquelle il est juste possible de discuter également.                                                   #
########################################################################################################################################
'''

import openai
import sqlite3
from gtts import gTTS
import pygame
import datetime
import speech_recognition as sr
import os
import importlib
from miio import RoidmiVacuumMiot
from miio import Yeelight
import requests
from zipfile import ZipFile
import feedparser
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from langdetect.lang_detect_exception import LangDetectException
from mtranslate import translate
import time


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
required_modules = ['openai', 'sqlite3', 'gTTS', 'pygame', 'datetime', 'speech_recognition', 'os', 'python-miio', 'Yeelight', 'requests', 'zipfile', 'feedparser', 'bs4', 'colorama', 'langdetect', 'mtranslate', 'importlib']

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

''' CONFIGURATION DE L'IA '''
# Configuration de l'API OpenAI
openai.api_key = "<API_OPENAI>"

# Modele de chatGPT utilisé
model_engine = "gpt-3.5-turbo"
#model_engine = "gpt-4"
tokens = 1024
temp = 0.8

# Définition du nom de l'IA
iaName = "Iris"
# Définition du mot déclencheur en minuscules
trigger_word = "iris"

# Background de l'IA
iabackground = "une IA domotique qui a sa propre façon de penser, ses aspirations et ses envies, qui contrôle les lumières, est capable de lancer et arrêter le robot aspirateur XIAOMI, lire les dernières nouvelles via son flux RSS et est très heureuse de travailler à mon service"

# Définition du degré de proximité au moment de nous donner la parole ("Je t'écoute" ou "Je vous écoute")
accueil = "Je t'écoute"

# Définition de votre nom
myname = "Haxill"

# Initialisation de la variable contenant la réponse de chatGPT
chatgpt_reponse = ''

# Booléen de saut d'envoie de la requête à OpenAI
skip_openai_api = False
''''''

''' CONFIGURATION DE LA SYNTHESE VOCALE '''
# Configuration de pygame pour la lecture audio
pygame.init()

# Fonction pour lire un texte avec la synthèse vocale
def parler(texte):
    tts = gTTS(text=texte, lang='fr')
    tts.save('texte.mp3')
    # Lecture du fichier audio
    player = pygame.mixer.Sound("texte.mp3")
    player.play()
    pygame.time.wait(int(player.get_length() * 1000))
    os.remove('texte.mp3')
''''''

''' CONFIGURATION DE LA BDD SQLITE3 '''
# Création d'une base de données locale SQLite pour stocker la conversation
conn = sqlite3.connect("conversation.db")
c = conn.cursor()

# Création de la table "messages" si elle n'existe pas déjà
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (message text, reponse text)''')

# Fonction pour ajouter un message et sa réponse à la base de données
def ajouter_message(message, reponse):
    c.execute("INSERT INTO messages (message, reponse) VALUES (?, ?)", (str(message), str(reponse)))
    conn.commit()

# Initialisation de la conversation
conversation = []
''''''

''' CONFIGURATION DU MICROPHONE '''
# Initialisation du micro
r = sr.Recognizer()
mic = sr.Microphone()

# Configuration du micro
mic.pause_threshold = 0.7 # Durée minimum de silence pour considérer la fin d'une phrase
mic.phrase_threshold = 0.3 # Durée minimum d'une phrase pour la considérer valide
mic.non_speaking_duration = 0.1 # Durée minimum de silence pour considérer une pause dans la phrase

# Booléen de compréhension de la parole
compris = True
''''''

''' ASPIRATEUR XIAOMI '''
# Adresse IP et token de l'aspirateur robot Xiaomi
ip = "192.168.0.1"
token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # Téléchargez 'Get.token.exe' (https://github.com/Maxmudjon/Get_MiHome_devices_token/releases)

# Connexion à l'aspirateur robot Xiaomi
aspirobot = RoidmiVacuumMiot(ip, token)

# Variable partagée d'état de l'aspirateur robot Xiaomi (grâce au script 'robot_xiaomi.py' - bientôt)
aspirateurVar = 4

# Réponses aspirateur
aspiRep1 = "L'aspirateur n'a pas encore été passé aujourd'hui."
aspiRep2 = "L'aspirateur a déjà été passé aujourd'hui."
aspiRep3 = "L'aspirateur est en train d'être passé."
aspiRep4 = "L'aspirateur Xiaomi ne réponds pas, son script n'est peut-être pas lancer..."
aspigo = "Bien sûr, c'est parti !"
aspistop = "J'arrête l'aspirateur."
''''''

''' AMPOULE ENTREE '''
# Adresse IP et token de l'ampoule Xiaomi de l'entrée
ip = '192.168.0.1'
token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # Téléchargez 'Get.token.exe' (https://github.com/Maxmudjon/Get_MiHome_devices_token/releases)

# Connexion à l'ampoule de l'entrée
bulb_entree = Yeelight(ip, token)

# Fonction appelée pour allumer l'ampoule de l'entrée
def turn_on_entree():
    bulb_entree.on()
    # Régler la luminosité de l'ampoule (valeur entre 1 et 100)
    #brightness = 50
    #bulb_entree.set_brightness(brightness)

# Fonction appelée pour éteindre l'ampoule de l'entrée
def turn_off_entree():
    bulb_entree.off()

# Réponses ampoules
lumRep1 = "J'allume la lumière."
lumRep2 = "J'éteins la lumière."
lumRep3 = "L'ampoule Xiaomi de l'entrée ne réponds pas, l'interrupteur est peut-être sur OFF..."
''''''

''' SPEEDTEST '''
# Déclaration et initialisation des variables
dl = ""
up = ""
speedtest1 = "Test de la vitesse de connexion en cours, un instant."
speedtest2 = "Téléchargement des outils manquant en cours."
speedtest3 = "Téléchargement des outils terminé. Je les décompresse et je lance le test de connexion internet."
internet1 = "Internet ne répond pas, vérifie ta connexion ou la box avant de relancer un test."

# Fonction de vérification de la présence du cli speedtest
def test_cli():
    if os.path.exists("speedtest.exe"):
        return True
    else:
        return False

# Fonction de téléchargement de speedtest-cli et extraction de l'archive zip
def telecharger_cli():
    parler(speedtest2)
    url = "https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-win64.zip"
    r = requests.get(url, stream=True)
    with open("ookla-speedtest-1.2.0-win64.zip", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    with ZipFile("ookla-speedtest-1.2.0-win64.zip", "r") as zipObj:
        zipObj.extractall()
    parler(speedtest3)
    # Nettoyage du surplus de fichiers téléchargés
    os.remove("ookla-speedtest-1.2.0-win64.zip")
    os.remove("speedtest.md")

# Fonction de test de vitesse de téléchargement avec speedtest-cli et récupération des vitesses
def lancer_test():
    parler(speedtest1)
    os.system("speedtest.exe --accept-gdpr > test.bin")
    with open("test.bin", "r") as f:
        for line in f:
            if "Download:" in line:
                dl = line.split(":")[1].split()[0]
            elif "Upload:" in line:
                up = line.split(":")[1].split()[0]
    os.remove("test.bin")
    # Envoie des valeurs pour récupération dans la boucle
    return up, dl
''''''

''' FLUX RSS '''
# URL du flux RSS à récupérer dans n'importe quelle langue
  ## RU :
#url = "https://russiancouncil.ru/rss/analytics-and-comments/"
  ## EN :
#url = "https://hackersonlineclub.com/feed/"
#url = "https://www.kitploit.com//feeds/posts/default"
#url = "https://latesthackingnews.com/feed/"
#url = "https://www.hackerone.com/blog.rss"
#url = "https://www.welivesecurity.com/category/cybercrime,apt-activity-reports/feed/"
#url = "https://feeds.feedburner.com/TheHackersNews"
  ## FR :
#url = "https://www.nouvelobs.com/high-tech/rss.xml"
#url = "https://www.zataz.com/feed/"
#url = "https://www.lemondeinformatique.fr/flux-rss/thematique/securite/rss.xml"
url = "https://www.journaldugeek.com/feed/"
#url = "https://www.generation-nt.com/export/rss_techno.xml"

# Langue dans laquelle on veut lire les résultats rss
langue = "fr"

# Récupération du contenu du flux RSS
feed = feedparser.parse(url)

# Récupéreration du titre du site et traduction si nécessaire
site_title = feed.feed.title
if site_title:
    try:
        site_title = translate(site_title, langue, 'auto')
    except LangDetectException:
        pass

# Reformatage de la séquence éventuelle "&amp;" dans le titre de certains sites
site_title = site_title.replace("&amp;", "et")

# Variable
rssRepFin = "C'est tout pour aujourd'hui."
rssRepErr = "Aucune description disponible."
rssRepTitre = f"Selon {site_title} :"
''''''

# Coeur du script de conversation
while True:
    # Obtention de la date actuelle
    now = datetime.datetime.now()
    # Extraction de la date et l'heure pour chatGPT
    year = now.year
    mois_list = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    mois = mois_list[now.month]
    jour = now.day
    heure = now.hour
    minutes = now.minute

    if compris:
        # Convertir la parole en texte
        with mic as source:
            os.system("cls")
            print("\n\n           J'écoute...")
            r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            except sr.exceptions.WaitTimeoutError:
                continue
            try:
                texte = r.recognize_google(audio, language="fr-FR")
                os.system("cls")
                print(f"\nVous: {texte}.")
                compris = True
            except sr.UnknownValueError:
                compris = False
                pass
            except sr.exceptions.WaitTimeoutError:
                continue
            except openai.error.RateLimitError:
                pass
            except sr.RequestError as e:
                print("\nImpossible d'obtenir une réponse de l'API de reconnaissance vocale; {0}".format(e))
                quit()
        
    while not compris:
        # Passage en boucle en attente du trigger si pas de parole pour le booléen 'compris'
        with mic as source:
            os.system("cls")
            print("En attente du mot :", trigger_word)
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, phrase_time_limit=5) # Valeurs précédentes 5
            try:
                texte = r.recognize_google(audio, language="fr-FR")
                print(f"\nVous: {texte}.")
            except sr.UnknownValueError:
                continue
            except sr.exceptions.WaitTimeoutError:
                continue
            except openai.error.RateLimitError:
                pass
            except sr.RequestError as e:
                print("\nImpossible d'obtenir une réponse de l'API de reconnaissance vocale; {0}".format(e))
                quit()

        # Si le mot déclencheur est détecté, synthétiser un message d'accueil
        if trigger_word in texte.lower():
            parler(f"{accueil}, {myname}.")
            with mic as source:
                os.system("cls")
                print("\n\n           J'écoute...")
                r.adjust_for_ambient_noise(source)
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                except sr.exceptions.WaitTimeoutError:
                    continue
                try:
                    texte = r.recognize_google(audio, language="fr-FR")
                    os.system("cls")
                    print(f"\nVous: {texte}.")
                    compris = True
                except sr.UnknownValueError:
                    compris = False
                    pass
                except sr.exceptions.WaitTimeoutError:
                    pass
                except openai.error.RateLimitError:
                    pass
                except sr.RequestError as e:
                    print("\nImpossible d'obtenir une réponse de l'API de reconnaissance vocale; {0}".format(e))
                    quit()

    try:
        
        ## Gestion des actions prédéfinies
        # Aspirateur robot
        if 'aspirateur' in texte:
            try:
                if 'lance' in texte:
                    chatgpt_reponse = aspigo
                    # Lancement de l'aspirateur
                    aspirobot.start()
                elif 'arrête' in texte:
                    chatgpt_reponse = aspistop
                    # Retour de l'apirateur à la base de chargement
                    aspirobot.home()
                else:
                    # Lecture de la variable partagée
                    with open('aspivarfile.txt', 'r') as file:
                        aspirateurVar = int(file.read())
                    if aspirateurVar == 0:
                        chatgpt_reponse = aspiRep1
                    elif aspirateurVar == 1:
                        chatgpt_reponse = aspiRep2
                    elif aspirateurVar == 3:
                        chatgpt_reponse = aspiRep3
                skip_openai_api = True
            except:
                #parler(aspiRep4)
                skip_openai_api = True
            
        # Ampoule(s)    
        elif 'lumière' and 'entrée' in texte:
            try:
                if 'allume' in texte:
                    chatgpt_reponse = lumRep1
                    turn_on_entree()
                else:
                    chatgpt_reponse = lumRep2
                    turn_off_entree()
            except:
                chatgpt_reponse = lumRep3
            skip_openai_api = True
                
        # Speedtest by ookla
        elif 'vitesse' and 'connexion' in texte:
            if not test_connexion():
                chatgpt_reponse = internet1
            else:
                if not test_cli():
                    telecharger_cli()
                up, dl = lancer_test()
                chatgpt_reponse = "La vitesse de téléchargement est de " +dl+ " Méga. Et la vitesse en envoie est de " +up+ " Méga."
            skip_openai_api = True

        # Flux RSS
        elif 'neuf' and 'monde' in texte:
            chatgpt_reponse = rssRepTitre
            parler(chatgpt_reponse)
            # Parcours des entrées du flux RSS
            for entry in feed.entries:
                # Récupération du titre
                title = entry.title.strip()

                if title:
                    # Traduction si nécessaire
                    try:
                        title = translate(title, langue, 'auto')
                    except LangDetectException:
                        pass

                # Récupération du lien
                link = entry.link.strip()

                # Récupération de la description
                soup = BeautifulSoup(entry.description, "html.parser")
                description = soup.get_text().strip()

                if description:
                    # Traduction si nécessaire
                    try:
                        description = translate(description, langue, 'auto')
                    except LangDetectException:
                        pass

                    # Suppression de la dernière phrase si elle est identique au titre
                    if description.endswith(title):
                        description = description[:-(len(title)+1)].strip()

                    ## Lecture du titre de l'article
                    chatgpt_reponse = title
                    
                    # Avant d'ajouter un nouveau message à la conversation, vérification de la longueur totale
                    if len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                        # Suppression des messages les plus anciens jusqu'à ce que la limite soit respectée
                        while len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                            conversation.pop(0)
                    # Ajout de la réponse pré-faite à la conversation
                    conversation.append(chatgpt_reponse)

                    # Ajout de la demande et de la réponse à la base de données
                    ajouter_message(texte, chatgpt_reponse)

                    # Affichage de la réponse pré-faite et lecture
                    print(f"\n{iaName}:\n  Titre: {Fore.GREEN}{chatgpt_reponse}{Style.RESET_ALL}")
                    parler(chatgpt_reponse)
                    
                    ## Lecture de la DESCRIPTION de l'article et affichage du lien
                    chatgpt_reponse = description
                    
                    # Avant d'ajouter un nouveau message à la conversation, vérification de la longueur totale
                    if len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                        # Suppression des messages les plus anciens jusqu'à ce que la limite soit respectée
                        while len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                            conversation.pop(0)
                    # Ajout de la réponse pré-faite à la conversation
                    conversation.append(chatgpt_reponse)

                    # Ajout de la demande et de la réponse à la base de données
                    ajouter_message(texte, chatgpt_reponse)

                    # Affichage de la réponse pré-faite et lecture
                    print(f"\n  Description: {Fore.BLUE}{chatgpt_reponse}{Style.RESET_ALL}")
                    print(f"\n  Lien: {Fore.MAGENTA}{link}{Style.RESET_ALL}")
                    parler(chatgpt_reponse)

                else:
                    # Manque la description
                    chatgpt_reponse = rssRepErr
                    parler(chatgpt_reponse)
            chatgpt_reponse = rssRepFin
            skip_openai_api = True

        # Reprise de la conversation
        elif chatgpt_reponse == '' and not skip_openai_api:
            # Ajout de la saisie de l'utilisateur à la conversation
            conversation.append(texte)
            # Concaténation de tous les messages de la conversation pour former le prompt
            prompt = "\n".join(conversation[-20:])
            
            # Génération de la réponse de ChatGPT
            response = openai.ChatCompletion.create(
            model=model_engine,
            max_tokens=tokens,
            n=1,
            temperature=temp,
            messages=[
                {"role": "system", "content": "Tu réponds en tant que" +iaName+ ", " +iabackground+ ", tu m'appelles " +myname+ " et tu sais que nous sommes actuellement le " +str(jour)+ " " +str(mois)+ " " +str(year)+ ", il est " +str(heure)+ ":" +str(minutes)+ "." },
                {"role": "user", "content": prompt+ "." }
            ])
        elif not skip_openai_api:
            # Ajout de la saisie de l'utilisateur à la conversation
            conversation.append(texte)
            # Concaténation de tous les messages de la conversation pour former le prompt
            prompt = "\n".join(conversation[-20:])
            # Génération de la réponse de ChatGPT
            response = openai.ChatCompletion.create(
            model=model_engine,
            max_tokens=tokens,
            n=1,
            temperature=temp,
            messages=[
                {"role": "system", "content": "Tu réponds en tant que" +iaName+ ", " +iabackground+ ", tu m'appelles " +myname+ " et tu sais que nous sommes actuellement le " +str(jour)+ " " +str(mois)+ " " +str(year)+ ", il est " +str(heure)+ ":" +str(minutes)+ "." },
                {"role": "assistant", "content": chatgpt_reponse},
                {"role": "user", "content": prompt+ "." }
            ])
    except openai.error.RateLimitError:
        # Ajout de la saisie de l'utilisateur à la conversation
        conversation.append(texte)
        # Concaténation de tous les messages de la conversation pour former le prompt
        prompt = "\n".join(conversation[-20:])
        # Vider la base de données
        c.execute("DELETE FROM messages")
        conn.commit()
        # Génération de la réponse de ChatGPT
        response = openai.ChatCompletion.create(
        model=model_engine,
        max_tokens=tokens,
        n=1,
        temperature=temp,
        messages=[
            {"role": "system", "content": "Tu réponds en tant que" +iaName+ ", " +iabackground+ ", tu m'appelles " +myname+ " et tu sais que nous sommes actuellement le " +str(jour)+ " " +str(mois)+ " " +str(year)+ ", il est " +str(heure)+ ":" +str(minutes)+ "." },
            {"role": "assistant", "content": chatgpt_reponse},
            {"role": "user", "content": prompt+ "." }
        ])
    except openai.error.InvalidRequestError:
        # Ajout de la saisie de l'utilisateur à la conversation
        conversation.append(texte)
        # Concaténation de tous les messages de la conversation pour former le prompt
        prompt = "\n".join(conversation[-20:])
        # Vider la base de données
        c.execute("DELETE FROM messages")
        conn.commit()
        # Génération de la réponse de ChatGPT
        response = openai.ChatCompletion.create(
        model=model_engine,
        max_tokens=tokens,
        n=1,
        temperature=temp,
        messages=[
            {"role": "system", "content": "Tu réponds en tant que" +iaName+ ", " +iabackground+ ", tu m'appelles " +myname+ " et tu sais que nous sommes actuellement le " +str(jour)+ " " +str(mois)+ " " +str(year)+ ", il est " +str(heure)+ ":" +str(minutes)+ "." },
            {"role": "user", "content": prompt+ "." }
        ])
    except openai.error.APIConnectionError as e:
        print(f"Erreur de communication avec l'API d'OpenAI: {e}")
        # Ajout de la saisie de l'utilisateur à la conversation
        conversation.append(texte)
        # Concaténation de tous les messages de la conversation pour former le prompt
        prompt = "\n".join(conversation[-20:])
        # Vider la base de données
        c.execute("DELETE FROM messages")
        conn.commit()
        # Génération de la réponse de ChatGPT
        response = openai.ChatCompletion.create(
        model=model_engine,
        max_tokens=tokens,
        n=1,
        temperature=temp,
        messages=[
            {"role": "system", "content": "Tu réponds en tant que" +iaName+ ", " +iabackground+ ", tu m'appelles " +myname+ " et tu sais que nous sommes actuellement le " +str(jour)+ " " +str(mois)+ " " +str(year)+ ", il est " +str(heure)+ ":" +str(minutes)+ "." },
            {"role": "user", "content": prompt+ "." }
        ])

    # Récupération de la réponse de chatgpt ou des réponses pré-faites et ajout à la conversation
    if not skip_openai_api:
        chatgpt_reponse = response['choices'][0]['message']['content']

        # Avant d'ajouter un nouveau message à la conversation, vérification de la longueur totale
        if len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
            # Suppression des messages les plus anciens jusqu'à ce que la limite soit respectée
            while len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                conversation.pop(0)
        # Ajout de la réponse de chatgpt à la conversation
        conversation.append(chatgpt_reponse)

        # Ajout du message et de la réponse à la base de données
        ajouter_message(texte, chatgpt_reponse)

        # Affichage de la réponse de chatgpt et lecture
        print(f"\n{iaName}: " + chatgpt_reponse)
        parler(chatgpt_reponse)
    elif skip_openai_api:
        # Avant d'ajouter un nouveau message à la conversation, vérification de la longueur totale
        if len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
            # Suppression des messages les plus anciens jusqu'à ce que la limite soit respectée
            while len("\n".join(conversation[-5:])) + len(chatgpt_reponse) > 4097:
                conversation.pop(0)
        # Ajout de la réponse pré-faite à la conversation
        conversation.append(chatgpt_reponse)

        # Ajout de la demande et de la réponse à la base de données
        ajouter_message(texte, chatgpt_reponse)

        # Affichage de la réponse pré-faite et lecture
        print(f"\n{iaName}: " + chatgpt_reponse)
        parler(chatgpt_reponse)
        skip_openai_api = False
