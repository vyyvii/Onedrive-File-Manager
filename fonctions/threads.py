# threads.py

# ===============
# === IMPORTS ===
# ===============
# Threading et interface web
import threading

# Interface graphique PyQt5
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

# Système et utilitaires
import sys
from io import BytesIO, StringIO
import requests
import time
import traceback
import sqlite3
from datetime import datetime, timedelta

# Correction des flux standards pour PyInstaller
# PyInstaller peut parfois définir sys.stderr/stdout/stdin à None
# Ce qui cause des erreurs avec certaines bibliothèques comme imagehash
if sys.stderr is None:
    sys.stderr = StringIO()
if sys.stdout is None:
    sys.stdout = StringIO()
if sys.stdin is None:
    sys.stdin = StringIO()

# Traitement d'images et détection de doublons
import imagehash
from PIL import Image
from itertools import combinations

# Modules locaux
from widgets import *
from fonctions.graph import *
from fonctions.logger import connecteLogger
from fonctions.sql import *

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

# ===============
# === THREADS ===
# ===============
class ParcoursPhotos(QObject):
    """
    Thread worker pour parcourir et analyser les photos/vidéos du OneDrive.
    
    Cette classe hérite de QObject et utilise les signaux PyQt pour communiquer
    avec l'interface utilisateur pendant le parcours des dossiers OneDrive.
    Elle analyse chaque fichier pour déterminer s'il s'agit d'une photo/vidéo,
    génère des hash perceptuels si demandé, et stocke les informations en base.
    
    Signaux:
        progression (str): Émet du texte pour afficher la progression
        image_ready (bytes): Émet les données d'image pour l'aperçu
        finished (): Signal émis à la fin du traitement
        
    Attributes:
        token (str): Token d'authentification Microsoft Graph API
        max_child (int): Nombre maximum d'enfants par dossier à traiter
        prev (bool): Active/désactive la génération de prévisualisations
        _pause_event (threading.Event): Contrôle la pause du traitement
        _stop_event (threading.Event): Contrôle l'arrêt du traitement
    """
    progression = pyqtSignal(str)    
    image_ready = pyqtSignal(bytes)
    finished = pyqtSignal()

    def __init__(self, token:str, types:list, prev:bool):
        """
        Initialise le worker de parcours des photos OneDrive.
        
        Args:
            token (str): Token d'authentification pour l'API Microsoft Graph
            types (list): Les types de médias à détecter
            prev (bool): Active la génération de prévisualisations et hash perceptuels
        """
        super().__init__()
        self.token = token # Token d'authentification Microsoft Graph
        self.types = types # Les types de médias à détecter
        self.prev = prev # Previsualisation des images activé TRUE/FALSE
        self.cache_empty = []
        
        # Événements de contrôle pour pause/arrêt
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._pause_event.set()  # Démarrage en mode actif
        
        logger.info(f"Initialisation ParcoursPhotos - types: {types}, preview: {prev}")

    def run(self):
        """
        Point d'entrée principal du thread de parcours OneDrive.
        
        Cette méthode:
        1. Se connecte à la base de données SQLite
        2. Récupère les dossiers racine via l'API Microsoft Graph
        3. Parcourt récursivement tous les dossiers trouvés
        4. Traite chaque fichier image/vidéo rencontré
        5. Génère des hash perceptuels si l'option preview est activée
        6. Stocke toutes les informations en base de données
        
        Le processus peut être mis en pause ou arrêté via les événements de contrôle.
        """
        logger.info("Début du parcours des photos OneDrive")
        self.start = time.time()

        # Connexion à la base de données locale
        try:
            self.connexion = sqlite3.connect("picture_video.db")
            self.curseur = self.connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BDD: {e}")
            self.progression.emit("Erreur d'accès à la base de données")
            return

        # Liste des IDs de dossiers à traiter
        self.list_id = []
        
        # Configuration de l'appel API initial (dossiers racine)
        endpoint = "me/drive/root/children/"
        select = ["name", "folder", "id", "file", "size", "createdDateTime", "lastModifiedDateTime", "parentReference"]

        logger.info("Appel API pour récupérer les dossiers racine")

        data = call_web_api(endpoint, self.token, select)

        if not data:
            logger.error(f"Erreur lors de l'appel API dossier {id}: {e}\n{traceback.format_exc()}")

        # Traitement des dossiers racine
        add_list_id = self.folder_list(data)
        self.list_id += add_list_id
        logger.info(f"Nombre de dossiers trouvés au niveau racine : {len(add_list_id)}")

        # Parcours récursif de tous les dossiers trouvés
        for id in self.list_id:
                # Vérification des événements de contrôle
                self._pause_event.wait()  # Attend si en pause

                if self._stop_event.is_set():
                    logger.info("Arrêt demandé par l'utilisateur")
                    break

                # Traitement du dossier courant
                endpoint = f"/me/drive/items/{id}/children"
                logger.debug(f"Traitement du dossier ID: {id}")

                data = call_web_api(endpoint, self.token, select)

                if not data:
                    logger.error(f"Erreur lors de l'appel API dossier {id}: {e}\n{traceback.format_exc()}")

                # Ajout des nouveaux dossiers trouvés à la liste
                add_id = self.folder_list(data)
                self.list_id += add_id

        logger.info(f"Parcours terminé - Total de dossiers traités : {len(self.list_id)}")
        self.end()

    def folder_list(self, data):
        """
        Traite les éléments d'un dossier OneDrive et détermine lesquels traiter.
        
        Pour chaque élément du dossier:
        - Si c'est un dossier avec peu d'enfants: l'ajoute à la liste de traitement
        - Si c'est un fichier image/vidéo: génère un hash perceptuel et l'enregistre en BDD
        - Sinon: ignore l'élément
        
        Args:
            data (dict): Réponse JSON de l'API Microsoft Graph contenant les éléments du dossier
            
        Returns:
            list: Liste des IDs de dossiers à traiter récursivement
        """
        list_id = []

        if data:
            # Parcours de chaque élément retourné par l'API
            for object in data.get('value', []):
                # Vérification des événements de contrôle
                self._pause_event.wait()

                if self._stop_event.is_set():
                    break

                # Extraction des informations de base
                name = object.get('name')
                id = object.get('id')
                path = object.get('parentReference').get('path')
                type = ""

                # Détermination du type de fichier (photo/vidéo/document)
                if object.get('file'):
                    type = self.is_picture_video_document(object)

                # Traitement des dossiers
                if object.get('folder'):
                    child = object.get('folder').get('childCount')

                    def emtpy_folder_treatment():
                        insert_sql_empty_folder(object, self.curseur, self.connexion)
                        self.progression.emit((f"NE CONTIENT AUCUN ENFANT : \n\nNom : {name} | ID : {id} | Type : {type} | Chemin : {path}/{name}\n"))
                        logger.info(f"{name} ne contient aucun enfant")

                    # Seulement les dossiers avec un nombre raisonnable d'enfants
                    if "Empty Folder" in self.types:
                        if child != 0:
                            if child < 5 and self.folder_is_empty(id):
                                emtpy_folder_treatment()

                            else:
                                logger.info(f"Nom : {name} | ID : {id} | Childs : {child}\n")
                                list_id.append(id)

                        elif child == 0 :
                            emtpy_folder_treatment()

                    else:
                        logger.info(f"Nom : {name} | ID : {id} | Childs : {child}\n")
                        list_id.append(id)

                # Traitement des fichiers images/vidéos/document
                elif object.get('file') and type in self.types:
                    phash = None

                    if type:
                        # Génération du hash perceptuel si prévisualisation activée
                        if self.prev:
                            try:
                                phash = self.preview(id, type)
                                logger.debug("La prévisualisation a fonctionné")

                            except Exception as e:
                                logger.error(f"La prévisualisation de {name} n'a pas fonctionné : {e}")

                    # Émission du signal de progression avec les détails du fichier
                    self.progression.emit((f"Nom : {name} | ID : {id} | Type : {type} | Chemin : {path}/{name}\n"))
                    
                    # Enregistrement en base de données
                    insert_sql(object, self.curseur, self.connexion, phash)

                else:
                    logger.info(f"{name} n'est ni une photo ni une vidéo")

        return list_id
    
    def is_picture_video_document(self, object):
        """
        Détermine si un fichier OneDrive est une image ou une vidéo.
        
        Utilise le type MIME du fichier pour classifier le contenu.
        
        Args:
            object (dict): Objet fichier de l'API Microsoft Graph
            
        Returns:
            str: "picture" si image, "video" si vidéo, None sinon
        """
        mime_type = object.get('file').get('mimeType')

        if mime_type.startswith("image/") == True:
            return "Images"
        
        elif mime_type.startswith("video/") == True:
            return "Vidéos"
        
        elif mime_type.startswith("application/") == True:
            return "Documents"

        else:
            return None
        
    def folder_is_empty(self, folder_id):
        """
        Vérifie récursivement si un dossier ne contient que des dossiers vides.
        
        Args:
            folder_id (str): ID du dossier à vérifier
            
        Returns:
            bool: True si le dossier est effectivement vide (ne contient que des dossiers vides), False sinon
        """
        if folder_id in self.cache_empty:
            return False
        
        else:
            self.cache_empty.append(folder_id)
            endpoint = f"/me/drive/items/{folder_id}/children"
            select = ["name", "folder", "id", "file", "size"]
        
            data = call_web_api(endpoint, self.token, select)

            if not data or not data.get("value"):
                return False
            
            logger.debug(f"Vérification de la capacité de {folder_id}")

            for child in data.get("value"):
                nom = child.get("name")
                logger.info(f"Test de {nom}")

                if child.get("file"):
                    logger.debug(f"{nom} contient un fichier")

                    return False
                
                elif child.get("folder"):
                    childcount = child.get("folder").get("childCount")

                    if childcount == 0:
                        logger.debug(f"{nom} contient {childcount} fichier")

                        continue

                    elif childcount > 0:
                        if not self.folder_is_empty(child.get("id")):
                            return False
            
            logger.debug(f"{folder_id} est vide avec {len(data.get("value"))} childs")
            return True

    def preview(self, id, type):
        """
        Génère une prévisualisation et un hash perceptuel pour un fichier.
        
        Cette méthode:
        1. Récupère une miniature via l'API Microsoft Graph
        2. Télécharge l'image de prévisualisation
        3. Émet un signal avec les données d'image pour l'interface
        4. Calcule un hash perceptuel pour les images (détection de doublons visuels)
        
        Args:
            id (str): ID unique du fichier OneDrive
            type (str): Type de fichier ("picture" ou "video")
            
        Returns:
            str: Hash perceptuel pour les images, None pour les vidéos ou en cas d'erreur
        """
        endpoint = f"me/drive/items/{id}/thumbnails"

        # Récupération des métadonnées de miniature
        data = call_web_api(endpoint, self.token)
        
        if not data:
            logger.warning(f"ERREUR : Aucune miniature disponible pour l'ID {id}\n{traceback.format_exc()}")
            return None 
            
        # URL de la miniature en grande taille
        url = data["value"][0]["large"]["url"]

        # Téléchargement de l'image de prévisualisation
        response = requests.get(url)
        image_data = response.content

        if image_data:
            logger.debug(f"Image data reçue, taille: {len(image_data)} bytes")
            
            # Émission du signal pour affichage dans l'interface
            self.image_ready.emit(image_data)
            
            # Calcul du hash perceptuel uniquement pour les images
            if type == "Images":
                logger.debug("Début traitement imagehash...")

                try:
                    img = Image.open(BytesIO(image_data))
                    
                    # Génération d'un hash perceptuel 16x16 pour la détection de doublons
                    hash_result = str(imagehash.phash(img, hash_size=16))
                    logger.debug(f"Hash calculé: {hash_result}")
                    return hash_result
                
                except Exception as e:
                    logger.error(f"Erreur conversion hash: {e}\n{traceback.format_exc()}")

            else:
                logger.debug("Type vidéo, pas de hash")
                return None       
        else:
            logger.warning(f"ERREUR : La preview de {id} n'a pas marché\n{traceback.format_exc()}")
            return None

    def end(self):
        """
        Finalise le processus de parcours et génère le rapport final.
        
        Cette méthode:
        1. Calcule la durée totale du traitement
        2. Compte le nombre total de fichiers traités
        3. Génère un résumé textuel des statistiques
        4. Émet les signaux de fin de traitement
        """
        end = time.time()
        duration = end - self.start

        # Nouvelle connexion pour le comptage final (thread-safe)
        try:
            connexion = sqlite3.connect("picture_video.db")
            curseur = connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BDD: {e}")
            self.progression.emit("Erreur d'accès à la base de données")
            return

        # Génération du rapport de fin
        texte = ""
        texte += f"Nombre de dossiers : {len(self.list_id)}"
        texte += f"\nNombre d'images et des videos : {compte_db(curseur)}"
        texte += f"\nCompte des photos fait en {duration:.2f} secondes"

        logger.info(f"Fin du parcours - Durée: {duration:.2f}s, Dossiers: {len(self.list_id)}, Fichiers: {compte_db(curseur)}")
        
        # Émission du résumé vers l'interface
        self.progression.emit(texte)

        # Signal de fin de traitement
        self.finished.emit()
        logger.info("Signal finished émis")

    def pause_clear(self):
        """Met en pause le parcours des photos en bloquant l'événement de pause."""
        self._pause_event.clear()
        logger.info("Pause du compte des photos")

    def pause_set(self):
        """Reprend le parcours des photos en libérant l'événement de pause."""
        self._pause_event.set()
        logger.info("Reprise du compte des photos")

    def stop(self):
        """Arrête définitivement le parcours et déclenche la finalisation."""
        self._stop_event.set()
        logger.info("Arrêt du compte des photos demandé")
        
        # Force la libération des événements de pause pour permettre l'arrêt
        self._pause_event.set()
        
        # Fermer la connexion à la base de données si elle existe
        try:
            if hasattr(self, 'connexion') and self.connexion:
                self.connexion.close()
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion BDD: {e}")
        
        # Émet le signal de fin pour nettoyer l'interface
        try:
            self.finished.emit()
        except Exception as e:
            logger.error(f"Erreur lors de l'émission du signal finished: {e}")
        
    def is_prev(self, prev):
        """
        Met à jour l'état de génération des prévisualisations.
        
        Args:
            prev (bool): Nouvel état de la prévisualisation
        """
        self.prev = prev

class ThreadPreview(QObject):
    """
    Thread worker pour générer des prévisualisations de comparaison de doublons.
    
    Cette classe génère les images de prévisualisation pour deux fichiers OneDrive
    afin de permettre à l'utilisateur de comparer visuellement les doublons potentiels.
    
    Signaux:
        image (tuple): Émet un tuple contenant (pixmap1, pixmap2, chemin1, chemin2)
        finished (): Signal émis à la fin de la génération des prévisualisations
        
    Attributes:
        token (str): Token d'authentification Microsoft Graph API
        id1, id2 (str): IDs des deux fichiers à comparer
        path1, path2 (str): Chemins complets des deux fichiers
    """
    image = pyqtSignal(tuple)    
    finished = pyqtSignal()

    def __init__(self, token, id1, id2, path1, path2):
        """
        Initialise le générateur de prévisualisations de comparaison.
        
        Args:
            token (str): Token d'authentification Microsoft Graph
            id1 (str): ID OneDrive du premier fichier
            id2 (str): ID OneDrive du second fichier  
            path1 (str): Chemin complet du premier fichier
            path2 (str): Chemin complet du second fichier
        """
        super().__init__()

        self.token = token
        self.id1 = id1
        self.id2 = id2
        self.path1 = path1
        self.path2 = path2
        logger.debug(f"ThreadPreview initialisé")

    def preview(self):
        """
        Génère les prévisualisations des deux fichiers et émet le résultat.
        
        Cette méthode télécharge les miniatures des deux fichiers via l'API
        Microsoft Graph et les convertit en objets QPixmap pour l'affichage.
        """
        logger.info("Début de génération des previews")
        
        # Génération des deux prévisualisations
        img1 = None
        if self.id1:
            img1 = self.preview_call(self.id1)
        
        img2 = None
        if self.id2:
            img2 = self.preview_call(self.id2)
        
        # Assemblage du tuple de résultat
        imgs_and_paths = (img1, img2, self.path1, self.path2)

        # Émission vers l'interface utilisateur
        self.image.emit(imgs_and_paths)
        logger.info("Previews générés et signal émis")
        self.finished.emit()
        
    def preview_call(self, id):
        """
        Génère une prévisualisation pour un fichier OneDrive spécifique.
        
        Args:
            id (str): ID unique du fichier OneDrive
            
        Returns:
            QPixmap: Image de prévisualisation, ou None en cas d'erreur
        """
        endpoint = f"me/drive/items/{id}/thumbnails"

        # Récupération des métadonnées de miniature
        data = call_web_api(endpoint, self.token)
        
        if not data or "value" not in data or not data["value"]:
            logger.warning(f"ERREUR : Aucune miniature disponible pour l'ID {id}\n{traceback.format_exc()}")
            return None 
            
        # URL de la miniature en grande taille
        url = data["value"][0]["large"]["url"]

        # Téléchargement de l'image
        response = requests.get(url)
        image_data = response.content

        if image_data:
            # Conversion en QPixmap pour PyQt5
            pixmap = QPixmap()
            
            if pixmap.loadFromData(image_data):
                return pixmap

class ThreadHashNomTaille(QObject):
    """
    Thread worker pour la détection de doublons par critères exacts.
    
    Cette classe recherche les doublons en comparant:
    - Les noms de fichiers identiques
    - Les tailles de fichiers identiques  
    - Les hash perceptuels identiques
    
    Elle évite les doublons de détection en vérifiant qu'une paire
    n'a pas déjà été identifiée par un autre critère.
    
    Signaux:
        progression (str, tuple, tuple): Émet les détails d'un doublon trouvé
        finished (): Signal émis à la fin de la recherche
    """
    progression = pyqtSignal(str, tuple, tuple)
    finished = pyqtSignal()

    def __init__(self):
        """Initialise le détecteur de doublons par critères exacts."""
        super().__init__()
        logger.debug("ThreadHashNomTaille initialisé")

    def hash_nom_taille(self):
        """
        Lance la recherche de doublons par nom, taille et hash perceptuel.
        
        Cette méthode:
        1. Se connecte à la base de données
        2. Récupère les doublons par nom+taille, taille seule, et hash seul
        3. Trie et déduplique les résultats pour éviter les doublons
        4. Émet un signal pour chaque paire de doublons trouvée
        """
        logger.info("Début de la recherche de doublons par nom, taille et hash")

        try:
            self.connexion = sqlite3.connect("picture_video.db")
            self.curseur = self.connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur BDD dans détection doublons: {e}")
            return

        # Récupération des différents types de doublons depuis la BDD
        doublons_from_nom = tri_doublons("name", "size", self.curseur)  # Nom ET taille identiques
        doublons_from_taille = tri_doublons("size", None, self.curseur)  # Taille seule
        doublons_from_hash = tri_doublons("hash", None, self.curseur)    # Hash perceptuel seul
        
        logger.debug(f"Doublons trouvés - Nom: {len(doublons_from_nom)}, Taille: {len(doublons_from_taille)}, Hash: {len(doublons_from_hash)}")

        # Liste finale des doublons uniques
        self.doublons_trouve = []

        # Traitement et déduplication
        self.tri(doublons_from_nom, "nom")
        self.tri(doublons_from_taille, "taille")
        self.tri(doublons_from_hash, "hash")
            
        # Émission des résultats vers l'interface
        if self.doublons_trouve:
            logger.info(f"Total de {len(self.doublons_trouve)} paires de doublons trouvées")
            
            for doublon in self.doublons_trouve:
                # Extraction des informations des deux fichiers
                photo1 = doublon["photo1"]
                photo2 = doublon["photo2"]
                nom1 = verification_len(photo1[0])
                nom2 = verification_len(photo2[0])
                id1 = photo1[3]
                id2 = photo2[3]
                ids = (id1, id2)

                # Génération du texte descriptif
                texte = ""
                texte += f"{nom1} ↔ {nom2}\n"
                texte += f"Critère: {doublon['critere']}\n"
                texte += f"Types: {photo1[1]} - {photo2[1]} | Tailles: {photo1[2]} - {photo2[2]}\n"
                texte += f"IDs: {id1} - {id2}\n"
                texte += f"Chemins: {verification_len(f"{photo1[4]}/{nom1}")} - {verification_len(f"{photo2[4]}/{nom2}")}\n"

                chemins = (f"{photo1[4]}/{nom1}", f"{photo2[4]}/{nom2}")
                self.progression.emit(texte, ids, chemins)
        else:
            # Aucun doublon trouvé
            logger.info("Aucun doublon trouvé par nom, taille et hash")
            texte = "Aucun doublon trouvé"
            ids = (None, None)
            chemins = (None, None)
            self.progression.emit(texte, ids, chemins)
        
        # Nettoyage
        if self.connexion:
            self.connexion.close()

        logger.info("ThreadHashNomTaille terminé")
        self.finished.emit()

    def tri(self, doublons_from, sort_type:str):
        """
        Trie une liste de doublons et les ajoute à la liste finale en évitant les duplicatas.
        
        Args:
            doublons_from (list): Liste des doublons trouvés par un critère spécifique
            sort_type (str): Type de critère utilisé ("nom", "taille", "hash")
        """
        # Traitement par paires (i, i+1)
        for i in range(0, len(doublons_from) - 1, 2):
            name1, type1, size1, id1, path1 = doublons_from[i]
            name2, type2, size2, id2, path2 = doublons_from[i + 1]

            # Vérification que cette paire n'a pas déjà été trouvée
            if not self.paire_existe(id1, id2):
                self.doublons_trouve.append({
                            'photo1': (name1, type1, size1, id1, path1),
                            'photo2': (name2, type2, size2, id2, path2),
                            'critere': f"{sort_type}"
                        })
                
    def paire_existe(self, id1, id2):
        """
        Vérifie si une paire de fichiers a déjà été identifiée comme doublon.
        
        Args:
            id1 (str): ID du premier fichier
            id2 (str): ID du second fichier
            
        Returns:
            bool: True si la paire existe déjà, False sinon
        """
        for doublon in self.doublons_trouve:
            id_doublon1 = doublon["photo1"][3]
            id_doublon2 = doublon["photo2"][3]

            # Vérification dans les deux sens (id1,id2) et (id2,id1)
            if (id_doublon1 == id1 and id_doublon2 == id2) or (id_doublon1 == id2 and id_doublon2 == id1):
                return True
            
        return False        

class ThreadVisuel(QObject):
    """
    Thread worker pour la détection de doublons visuels par similarité.
    
    Cette classe utilise les hash perceptuels pour détecter les images
    visuellement similaires même si elles ont été modifiées (compression,
    redimensionnement, légers ajustements, etc.).
    
    L'algorithme calcule plusieurs métriques de similarité:
    - Similarité de base basée sur la distance de Hamming
    - Similarité fine bit par bit
    - Similarité par clusters de bits
    
    Signaux:
        progression (str, tuple, tuple): Émet les détails d'un doublon visuel trouvé
        finished (): Signal émis à la fin de la recherche
        
    Attributes:
        seuil (int): Seuil de distance maximale pour considérer deux images similaires
    """
    progression = pyqtSignal(str, tuple, tuple)
    finished = pyqtSignal()

    def __init__(self, seuil):
        """
        Initialise le détecteur de doublons visuels.
        
        Args:
            seuil (int): Distance maximale entre hash pour considérer deux images similaires
                        (plus le seuil est bas, plus la détection est stricte)
        """
        super().__init__()
        self.seuil = seuil
        logger.debug(f"ThreadVisuel initialisé avec seuil: {seuil}")

    def distance(self):
        """
        Lance la recherche de doublons visuels par comparaison de hash perceptuels.
        
        Cette méthode:
        1. Récupère tous les hash perceptuels depuis la base de données
        2. Compare chaque paire d'images via leur hash perceptuel
        3. Calcule plusieurs métriques de similarité pour chaque paire
        4. Identifie les doublons selon le seuil configuré
        5. Émet un signal pour chaque doublon visuel trouvé
        """
        logger.info(f"Début de la recherche de doublons visuels avec seuil: {self.seuil}")
        self.connexion = sqlite3.connect("picture_video.db")
        self.curseur = self.connexion.cursor()

        # Récupération de toutes les images avec hash perceptuel
        self.image_phash = recup_phash(self.curseur)
        logger.info(f"Nombre d'images avec hash perceptuel: {len(self.image_phash)}")
        self.doublons_trouve = []

        # Comparaison de toutes les paires possibles d'images
        for img1, img2 in combinations(self.image_phash, 2):
            name1, type1, size1, id1, phash1, path1 = img1
            name2, type2, size2, id2, phash2, path2 = img2

            # Conversion des hash hexadécimaux en objets ImageHash
            hash1 = imagehash.hex_to_hash(phash1)
            hash2 = imagehash.hex_to_hash(phash2)
            
            # Calcul de la distance de Hamming entre les deux hash
            distance = hash1 - hash2

            # Si la distance est inférieure au seuil, c'est un doublon potentiel
            if distance <= self.seuil:
                hash_size = len(hash1.hash.flat)
                
                # === CALCUL DE SIMILARITÉ BASE ===
                # Pourcentage basé sur la distance de Hamming
                similarite_base = max(0.0, (hash_size - float(distance)) / hash_size * 100.0)
                
                # === CALCUL DE SIMILARITÉ FINE ===
                # Comparaison bit par bit pour plus de précision
                bits_identiques = sum(1 for i in range(hash_size) if hash1.hash.flat[i] == hash2.hash.flat[i])
                similarite_fine = (bits_identiques / hash_size) * 100.0
                
                # === CALCUL DE SIMILARITÉ PAR CLUSTERS ===
                # Analyse par groupes de bits pour détecter les similitudes locales
                clusters_similaires = 0
                cluster_size = 4 
                for i in range(0, hash_size, cluster_size):
                    cluster1 = hash1.hash.flat[i:i+cluster_size]
                    cluster2 = hash2.hash.flat[i:i+cluster_size]
                    # Un cluster est similaire si 75% de ses bits correspondent
                    if sum(cluster1 == cluster2) >= cluster_size * 0.75:
                        clusters_similaires += 1
                
                similarite_clusters = (clusters_similaires / (hash_size // cluster_size)) * 100.0
                
                # === CALCUL DE SIMILARITÉ GLOBALE ===
                # Moyenne pondérée des trois métriques
                if similarite_clusters and similarite_fine and similarite_base:
                    similarite = (similarite_base * 0.5 + similarite_fine * 0.3 + similarite_clusters * 0.2)
                else:
                    similarite = similarite_base

                # Ajout du doublon à la liste
                self.doublons_trouve.append({
                        'photo1': (name1, type1, size1, id1, path1),
                        'photo2': (name2, type2, size2, id2, path2),
                        'distance': distance,
                        'similarite': similarite
                    })
                
                logger.info(f"Doublon trouvé : {name1} avec {name2}")

        # Émission des résultats vers l'interface
        if self.doublons_trouve:
            logger.info(f"Total de {len(self.doublons_trouve)} doublons visuels trouvés")
            
            for doublon in self.doublons_trouve:
                doublon1 = doublon["photo1"]
                doublon2 = doublon["photo2"]
                nom1 = doublon1[0]
                nom2 = doublon2[0]
                id1 = doublon1[3]
                id2 = doublon2[3]
                ids = (id1, id2)

                # Génération du texte descriptif avec métriques de similarité
                texte = ""
                texte += f"{verification_len(doublon1[0])} ↔ {verification_len(doublon2[0])}\n"
                texte += f"Similarité: {doublon['similarite']:.2f}% | Distance: {doublon['distance']}\n"
                texte += f"Types: {doublon1[1]} - {doublon2[1]} | Tailles: {doublon1[2]} - {doublon2[2]}\n"
                texte += f"IDs: {id1} - {id2}\n"
                texte += f"Chemins: {verification_len(f"{doublon1[4]}/{nom1}")} - {verification_len(f"{doublon2[4]}/{nom2}")}\n"

                chemins = (f"{doublon1[4]}/{nom1}", f"{doublon2[4]}/{nom2}")
                self.progression.emit(texte, ids, chemins)
        else:
            # Aucun doublon visuel trouvé
            logger.warning("Aucun doublon visuel trouvé")
            texte = "Aucun doublon n'a été trouvé !\n"
            texte += "Vérifiez que vous avez bien activé l'option de prévisualisation des images !\n"
            ids = (None, None)
            chemins = (None, None)
            self.progression.emit(texte, ids, chemins)

        # Nettoyage
        if self.connexion:
            self.connexion.close()

        logger.info("ThreadVisuel terminé")
        self.finished.emit()

class ThreadUseless(QObject):
    progression = pyqtSignal(str, tuple, tuple)    
    finished = pyqtSignal()

    def __init__(self, mode, max_size = 1000, years = 4):
        super().__init__()   
        self.mode = mode
        self.inutile: list[dict] = []
        self.years = years
        self.max_size = max_size

        # Connexion à la base de données locale
        try:
            connexion = sqlite3.connect("picture_video.db")
            curseur = connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BDD: {e}")
            self.progression.emit("Erreur d'accès à la base de données")
            return

        if curseur:
            self.db = recup_useless(curseur)   

        # Nettoyage
        if connexion:
            connexion.close()

    def run(self):
        if self.mode == "ext":
            self.extension()

        elif self.mode == "siz":
            self.size()
        
        elif self.mode == "old":
            self.anciennete()

        elif self.mode == "two":
            self.extension()
            self.size()

        elif self.mode == "all":
            self.extension()
            self.size()
            self.anciennete()

        self.affichage_resultat()

        self.finished.emit() 

    def extension(self):
        extensions_useless = [
            ".gifs", 
            ".tmp", 
            ".temp", 
            ".cache", 
            ".bak", 
            ".old", 
            ".log", 
            ".dmp", 
            ".crash", 
            ".crdownload", 
            ".partial", 
            "._", 
            ".thumb", 
            ".DS_store", 
            ".localized", 
            ".ini"
            ]

        for element in self.db:
            for ext in extensions_useless:
                if element[0].endswith(ext):
                    element_append = {
                                'nom': element[0],
                                'type': element[1],
                                'size':  element[2],
                                'id':  element[3],
                                'path': element[4],
                                'lastModified': element[5],
                                'detection': "ext"
                            }
                    if element_append not in self.inutile:
                        self.inutile.append(element_append)

    def size(self):
        for element in self.db:
            if element[2] < 1000:
                element_append = {
                                'nom': element[0],
                                'type': element[1],
                                'size':  element[2],
                                'id':  element[3],
                                'path': element[4],
                                'lastModified': element[5],
                                'detection': "siz"
                            }
                if element_append not in self.inutile:
                    self.inutile.append(element_append)

    def anciennete(self):
        self.years_ago = (datetime.now() - timedelta(days=365 * self.years)).isoformat()

        for element in self.db:
            if element[5] < self.years_ago:
                element_append = {
                                'nom': element[0],
                                'type': element[1],
                                'size':  element[2],
                                'id':  element[3],
                                'path': element[4],
                                'lastModified': element[5],
                                'detection': "old"
                            }
                if element_append not in self.inutile:
                    self.inutile.append(element_append)

    def affichage_resultat(self):
        # Émission des résultats vers l'interface
        if self.inutile:
            logger.info(f"Total de {len(self.inutile)} fichiers inutiles trouvés")
            
            for fichier_inutile in self.inutile:
                nom = verification_len(fichier_inutile['nom'])
                id = verification_len(fichier_inutile['id'])
                path = verification_len(fichier_inutile['path'])
                chemin_complet = verification_len(f"{path}/{nom}")

                # Génération du texte descriptif avec métriques de similarité
                texte = ""
                
                if fichier_inutile['detection'] == "ext":
                    texte += "=== Fichier avec une extension inutile === \n\n"

                elif fichier_inutile['detection'] == "siz":
                    texte += f"=== Fichier très petit (< {self.max_size/1000}Kb) === \n\n"

                elif fichier_inutile['detection'] == "old":
                    texte += f"=== Fichier vieux d'il y a plus de {self.years} ans === \n\n"

                texte += f"Nom: {nom}\n"
                texte += f"Taille: {fichier_inutile['size']}\n"
                texte += f"ID: {id}\n"
                texte += f"Chemin:\n{chemin_complet}\n"
                texte += f"Dernière utilisation: {fichier_inutile['lastModified']}\n"

                ids = (id, None)
                chemins = (f"{fichier_inutile['path']}/{fichier_inutile['nom']}", None)
                self.progression.emit(texte, ids, chemins)

        else:
            # Aucun fichier inutile
            logger.warning("Aucun fichier inutile trouvé")
            texte = "Aucun fichier inutile n'a été trouvé !\n"
            ids = (None, None)
            chemins = (None, None)
            self.progression.emit(texte, ids, chemins)

def verification_len(data):
    len_max = 45
    if len(data) <= len_max:
        return data
    
    # Liste des séparateurs à essayer par ordre de priorité
    separateurs = ['/', '_', '.']
    
    # Trouver quel séparateur est le plus fréquent dans data
    meilleur_sep = '/'
    max_count = 0
    
    for sep in separateurs:
        count = data.count(sep)
        if count > max_count:
            max_count = count
            meilleur_sep = sep
    
    # Si aucun séparateur trouvé, retourner tel quel
    if max_count == 0:
        return data
    
    parties = data.split(meilleur_sep)
    chemin_affiche = ""
    ligne_courante = ""
    for partie in parties:
        # Tester si ajouter cette partie dépasse la limite
        if ligne_courante:
            test_ligne = ligne_courante + meilleur_sep + partie
        else:
            test_ligne = partie
            
        if len(test_ligne) > len_max:
            # Cette partie fait déborder, on termine la ligne courante
            if chemin_affiche:
                chemin_affiche += "\n" + ligne_courante
            else:
                chemin_affiche = ligne_courante
            
            # Commencer une nouvelle ligne avec la partie actuelle
            ligne_courante = partie
        else:
            # On peut ajouter cette partie à la ligne courante
            ligne_courante = test_ligne
    
    # Ajouter la dernière ligne
    if ligne_courante:
        if chemin_affiche:
            chemin_affiche += "\n" + ligne_courante
        else:
            chemin_affiche = ligne_courante
    
    return chemin_affiche