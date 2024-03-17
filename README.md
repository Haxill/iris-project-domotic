# Projet d'IA Domotique Configurable

## Description
Ce projet est une application d'IA domotique configurable, contrôlable vocalement et capable de répondre vocalement. Il permet de gérer divers aspects tels que l'éclairage, le robot aspirateur Xiaomi, les tests de vitesse de connexion, la lecture et la traduction des nouvelles d'un flux RSS, ainsi que des conversations générales.
Afin de faire fonctionner la connexion avec le robot aspirateur Xiaomi, il faut lancer le script "aspirateur_xiaomi.py" en parallèle du script principal "Iris-GPT4.py" (partageant des variables).

## Configuration Requise
- Système d'exploitation: Windows 10 / Windows 11
- Python: Version 3.9.13
- Modules externes: openai, sqlite3, gTTS, pygame, datetime, speech_recognition, os, miio, Yeelight, requests, zipfile, feedparser, bs4, colorama, langdetect, mtranslate

## Installation des Modules
L'installation des modules se fait automatiquement, après un test de connexion internet, en lançant le script.
```bash
pip install openai sqlite3 gTTS pygame datetime SpeechRecognition python-miio Yeelight requests zipfile feedparser beautifulsoup4 colorama langdetect mtranslate
```

## Configuration de l'IA
- Clé API OpenAI: Remplacez `<API_OPENAI>` dans le script "Iris-GPT4.py" par votre clé API OpenAI.
- Modèle d'OpenAI: Vous pouvez remplacer le `model_engine` par gpt-4, si vous le souhaitez.
- Token et IPs: Assurez-vous de remplacer `token` par vos propres tokens et `ip` par vos adresses IP.
- Votre Nom: Remplacer `myname` par le nom par lequel vous souhaitez que l'IA vous appelle.

## Utilisation
1. Exécutez le script "Iris-GPT4.py" dans un environnement Python 3.9.13 sous WIndows 10 ou 11.
2. Le script vérifie que vous avez internet sinon s'arrête.
3. Il vérifie la présence des modules, sinon les installes.
4. Suivez les instructions vocales pour interagir avec l'IA.

## Fonctionnalités Principales
- Contrôle de l'éclairage Xiaomi
- Gestion du robot aspirateur Xiaomi
- Tests de vitesse de connexion
- Lecture et traduction des actualités d'un flux RSS
- Conversations générales avec l'IA

## Auteurs
- HAXILL

## Version
- 28/01/2024

## Licence
Ce script est sous licence [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) - voir le fichier [LICENSE](https://github.com/Haxill/iris-project-domotic/blob/main/LICENSE) pour plus de détails.
