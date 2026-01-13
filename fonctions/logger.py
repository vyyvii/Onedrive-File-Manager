# logger.py
import logging
import os
import sys
from datetime import datetime

def connecteLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Créer le dossier /logs s'il n'existe pas
        # Gestion spéciale pour les exe PyInstaller
        if getattr(sys, 'frozen', False):
            # Si on est dans un exe PyInstaller
            base_path = os.path.dirname(sys.executable)
        else:
            # Si on est en développement
            base_path = os.path.dirname(os.path.dirname(__file__))
        
        cheminLogs = os.path.join(base_path, "logs")
        os.makedirs(cheminLogs, exist_ok=True)

        # Créer un nom de fichier unique avec date + heure
        datePrecise = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nomFichierLog = os.path.join(cheminLogs, f"log_{datePrecise}.log")

        # Créer le FileHandler
        gestionnaireFichiers = logging.FileHandler(nomFichierLog, encoding='utf-8')
        gestionnaireFichiers.setLevel(logging.DEBUG)

        # Format des logs
        formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        gestionnaireFichiers.setFormatter(formatter)

        logger.addHandler(gestionnaireFichiers)

        # Supprimer les anciens fichiers si plus de 5
        fichiers_logs = sorted(
            [f for f in os.listdir(cheminLogs) if f.endswith('.log')],
            key=lambda f: os.path.getmtime(os.path.join(cheminLogs, f))
        )

        while len(fichiers_logs) > 5:
            fichier_a_supprimer = fichiers_logs.pop(0)
            os.remove(os.path.join(cheminLogs, fichier_a_supprimer))

    return logger
