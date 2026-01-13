# ===============
# === IMPORTS ===
# ===============
# Interface graphique PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QThread, QTimer

# Système et utilitaires
import sys
from io import StringIO
import traceback

# Correction des flux standards pour PyInstaller
# PyInstaller peut parfois définir sys.stderr/stdout/stdin à None
# Ce qui cause des erreurs avec certaines bibliothèques comme imagehash
if sys.stderr is None:
    sys.stderr = StringIO()
if sys.stdout is None:
    sys.stdout = StringIO()
if sys.stdin is None:
    sys.stdin = StringIO()

# Modules locaux
import style
from widgets import *
from fonctions.graph import *
from fonctions.logger import connecteLogger
from fonctions.sql import *
from fonctions.threads import *

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

# ================
# === DOUBLONS ===
# ================
class Doublons(QWidget):
    """
    Interface de gestion des doublons détectés.
    
    Cette classe fournit une interface complète pour:
    - Lancer différents types de détection de doublons
    - Visualiser les doublons trouvés dans une liste scrollable
    - Comparer visuellement deux fichiers doublons
    - Naviguer entre les différents doublons
    - Supprimer les fichiers indésirables directement depuis OneDrive
    
    L'interface se compose de:
    - Boutons de lancement des détections (nom/taille/hash et visuel)
    - Zone d'affichage des images de comparaison
    - Liste scrollable des doublons avec navigation
    - Contrôles de suppression et navigation
    
    Attributes:
        token (str): Token d'authentification Microsoft Graph
        parent_interface: Référence vers l'interface principale
        current_number (int): Numéro du doublon actuellement affiché
        current_displayed_doublon (int): Index du doublon visible à l'écran
        doublons_liste (list): Liste de tous les doublons trouvés
    """
    def __init__(self, token, parent=None):
        """
        Initialise l'interface de gestion des doublons.
        
        Args:
            token (str): Token d'authentification Microsoft Graph
            parent: Widget parent (interface principale)
        """
        super().__init__(parent)
        logger.info("Initialisation de la classe Doublons")
        self.token = token
        self.parent_interface = parent
        
        # État de navigation dans les doublons
        self.current_number = 0
        self.current_displayed_doublon = 0
        self.doublons_liste = []
        self.is_suppr = False
        logger.debug(f"Doublons initialisé avec parent: {parent is not None}")
        
        # Eléments de la page
            # Textes informatifs
        titre = Text("Gestion des Doublons", style.cssTitre)
        sous_titre = Text("Avec quelle méthode souhaitez vous trouver les doublons ?", style.cssSousTitre)

            # Boutons de contrôle principal
        self.bouton_hash_nom_taille = Bouton("Nom, taille et hash", self.hash_nom_taille, True, 350)
        self.bouton_visuel = Bouton("Visuel", self.visuel)
        self.bouton_empty_folder = Bouton("Dossiers vides", self.empty_folder_view)
        self.bouton_inutile = Bouton("Inutile", self.useless)
        self.bouton_suppression1 = Bouton("Supprimer", None, False)  # Dynamiquement connecté
        self.bouton_suppression2 = Bouton("Supprimer", None, False)  # Dynamiquement connecté
        self.bouton_retour = Bouton("Retour à l'accueil", self.retour_accueil)

        self.verif_boutons()
        
            # Boutons de navigation entre doublons
        self.bouton_precedent = Bouton("Précédent", None, False, 150)  # Dynamiquement connecté
        self.bouton_suivant = Bouton("Suivant", None, False, 150)      # Dynamiquement connecté

            # Zones d'affichage des images de comparaison
        self.label_image_doublons_1 = LabelImage(600, 500)
        self.label_image_doublons_2 = LabelImage(600, 500)

            # Labels pour afficher les chemins des fichiers sous les images
        self.label_chemin_1 = Text("", style.cssPath)
        self.label_chemin_1.setWordWrap(True)
        self.label_chemin_1.setMaximumWidth(600)
        self.label_chemin_1.setAlignment(Qt.AlignCenter)
        
        self.label_chemin_2 = Text("", style.cssPath)
        self.label_chemin_2.setWordWrap(True)
        self.label_chemin_2.setMaximumWidth(600)
        self.label_chemin_2.setAlignment(Qt.AlignCenter)

            # Zone de liste scrollable pour afficher tous les doublons
        self.scroll_area = ScrollArea(600, 540, True)
        self.scroll_container = QWidget()
        self.vbox = QVBoxLayout(self.scroll_container)
        self.scroll_area.setWidget(self.scroll_container)
        
        # Layout principal et conteneurs
        layout_doublons = QVBoxLayout()
        layout_boutons = QHBoxLayout()
        layout_texte_pixmap = QHBoxLayout()
        layout_scroll_zone = QVBoxLayout()
        layout_boutons_suivant_precedent = QHBoxLayout()

        # Conteneurs avec politique de taille fixe
        bouton_container = QWidget()
        bouton_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        texte_pixamp_container = QWidget()
        texte_pixamp_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        scroll_zone_container = QWidget()
        scroll_zone_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        suivant_precedent_container = QWidget()
        suivant_precedent_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Configuration du layout des boutons de contrôle
        layout_boutons.setContentsMargins(5, 5, 5, 5)
        layout_boutons.setSpacing(5)
        layout_boutons.addWidget(self.bouton_hash_nom_taille)
        layout_boutons.addWidget(self.bouton_visuel)
        layout_boutons.addWidget(self.bouton_empty_folder)
        layout_boutons.addWidget(self.bouton_inutile)
        bouton_container.setLayout(layout_boutons)
        
        # Container pour la première image + chemin + bouton suppression
        image1_container = QWidget()
        image1_layout = QVBoxLayout(image1_container)
        image1_layout.setContentsMargins(5, 5, 5, 5)
        image1_layout.setSpacing(5)
        image1_layout.addWidget(self.label_image_doublons_1)
        image1_layout.addWidget(self.label_chemin_1)
        image1_layout.addWidget(self.bouton_suppression1, 0, Qt.AlignCenter)
        
        # Container pour la seconde image + chemin + bouton suppression
        image2_container = QWidget()
        image2_layout = QVBoxLayout(image2_container)
        image2_layout.setContentsMargins(5, 5, 5, 5)
        image2_layout.setSpacing(5)
        image2_layout.addWidget(self.label_image_doublons_2)
        image2_layout.addWidget(self.label_chemin_2)
        image2_layout.addWidget(self.bouton_suppression2, 0, Qt.AlignCenter)

        # Layout des boutons de navigation entre doublons
        layout_boutons_suivant_precedent.setContentsMargins(5, 5, 5, 5)
        layout_boutons_suivant_precedent.setSpacing(10)
        layout_boutons_suivant_precedent.addWidget(self.bouton_precedent)
        layout_boutons_suivant_precedent.addWidget(self.bouton_suivant)
        suivant_precedent_container.setLayout(layout_boutons_suivant_precedent)

        # Layout de la zone de liste scrollable
        layout_scroll_zone.setContentsMargins(5, 5, 5, 5)
        layout_scroll_zone.setSpacing(5)
        layout_scroll_zone.addWidget(self.scroll_area)
        layout_scroll_zone.addWidget(suivant_precedent_container, 0, Qt.AlignCenter)
        scroll_zone_container.setLayout(layout_scroll_zone)
        
        # Layout principal avec images et liste
        layout_texte_pixmap.setContentsMargins(5, 5, 5, 5)
        layout_texte_pixmap.setSpacing(5)
        layout_texte_pixmap.addWidget(image1_container)
        layout_texte_pixmap.addWidget(image2_container)
        layout_texte_pixmap.addWidget(scroll_zone_container)
        texte_pixamp_container.setLayout(layout_texte_pixmap)

        # Assemblage final de l'interface
        layout_doublons.addWidget(titre, 0, Qt.AlignCenter)
        layout_doublons.addWidget(sous_titre, 0, Qt.AlignCenter)
        layout_doublons.addWidget(bouton_container, 0, Qt.AlignCenter)
        layout_doublons.addWidget(texte_pixamp_container, 0, Qt.AlignCenter)
        layout_doublons.addWidget(self.bouton_retour, 0, Qt.AlignCenter)

        self.setLayout(layout_doublons)

    def verif_boutons(self):
        try:
            connexion = sqlite3.connect("picture_video.db")
            curseur = connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BDD: {e}")

        len_db_picture_video = 0
        phash = []
        len_db_empty_folder = 0

        if curseur:
            len_db_picture_video = compte_db(curseur)
            phash = recup_phash(curseur)
            len_db_empty_folder = compte_db(curseur, db = "empty_folder")

            logger.debug(f"len de picture_video: {len_db_picture_video} | len de empty_folder: {len_db_empty_folder} | nombre de phash: {len(phash)}")
        
        if len_db_picture_video != 0:
            self.bouton_hash_nom_taille.set_button(True)
            self.etat_bouton_hash_nom_taille = True

        else:
            self.bouton_hash_nom_taille.set_button(False)
            self.etat_bouton_hash_nom_taille = False

        if phash != []:
            self.bouton_visuel.set_button(True)
            self.etat_bouton_visuel = True

        else:
            self.bouton_visuel.set_button(False)
            self.etat_bouton_visuel = False

        if len_db_empty_folder != 0:
            self.bouton_empty_folder.set_button(True)
            self.etat_bouton_empty_folder = True

        else:
            self.bouton_empty_folder.set_button(False)
            self.etat_bouton_empty_folder = False

        if len_db_picture_video != 0:
            self.bouton_inutile.set_button(True)
            self.etat_bouton_useless = True

        else:
            self.bouton_inutile.set_button(False)
            self.etat_bouton_useless = False

        logger.info("Les boutons de la pages doublons ont étés actualisés")

    def hash_nom_taille(self):
        """
        Lance la détection de doublons par critères exacts (nom, taille, hash).
        
        Cette méthode:
        1. Remet à zéro l'état de navigation et vide la liste des doublons
        2. Désactive temporairement l'interface pendant le traitement
        3. Lance un thread de détection ThreadHashNomTaille
        4. Configure les connexions de signaux pour recevoir les résultats
        """
        self.stop_existing_thread('thread_hash')

        # Réinitialisation de l'état
        self.begin()
        self.current_number = 0
        self.current_displayed_doublon = 0
        self.doublons_liste =  []

        # Nettoyage de la liste précédente
        while self.vbox.count():
            child = self.vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Configuration et lancement du thread de détection
        self.thread_hash = QThread()
        self.worker_hash = ThreadHashNomTaille()
        self.worker_hash.moveToThread(self.thread_hash)

        # Connexions des signaux
        self.worker_hash.progression.connect(self.ajouter_layout)
        self.thread_hash.started.connect(self.worker_hash.hash_nom_taille)
        self.worker_hash.finished.connect(self.thread_hash.quit)
        self.worker_hash.finished.connect(self.worker_hash.deleteLater)
        self.thread_hash.finished.connect(self.thread_hash.deleteLater)
        self.thread_hash.finished.connect(self.end)

        self.thread_hash.start()

    def visuel(self):
        """
        Lance la détection de doublons visuels par similarité de hash perceptuels.
        
        Similaire à hash_nom_taille() mais utilise ThreadVisuel avec le seuil
        de similarité configuré par l'utilisateur via self.seuil_spin.
        """
        self.stop_existing_thread('thread_visuel')

        # Pop-up pour demander le seuil
        seuil, ok = InputDialog.getInt(
            self,
            "Seuil visuel", 
            "Choisissez le seuil de similarité (0-100):", 
            20,  # Valeur par défaut
            0, 
            100
        )
        
        if not ok:  # Utilisateur a annulé
            return

        # Réinitialisation de l'état
        self.begin()
        self.current_number = 0
        self.current_displayed_doublon = 0
        self.doublons_liste =  []

        # Nettoyage de la liste précédente
        while self.vbox.count():
            child = self.vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Configuration et lancement du thread de détection visuelle
        self.thread_visuel = QThread()
        self.worker_visuel = ThreadVisuel(seuil)  # Passage du seuil de similarité
        self.worker_visuel.moveToThread(self.thread_visuel)

        # Connexions des signaux
        self.worker_visuel.progression.connect(self.ajouter_layout)
        self.thread_visuel.started.connect(self.worker_visuel.distance)
        self.worker_visuel.finished.connect(self.thread_visuel.quit)
        self.worker_visuel.finished.connect(self.worker_visuel.deleteLater)
        self.thread_visuel.finished.connect(self.thread_visuel.deleteLater)
        self.thread_visuel.finished.connect(self.end)

        self.thread_visuel.start()

    def empty_folder_view(self):
        """
        Lance la détection des dossiers vides
        """
        self.current_number = 0
        self.current_displayed_doublon = 0
        self.doublons_liste =  []

        # Nettoyage de la liste précédente
        while self.vbox.count():
            child = self.vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Connexion à la base de données locale
        try:
            connexion = sqlite3.connect("picture_video.db")
            curseur = connexion.cursor()

        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BDD: {e}")
            return
        
        empty_folder = recup_folder(curseur)

        if empty_folder:
            for element in empty_folder:
                id = element[0]
                name = element[1]
                size = element[2]
                path = element[3]

                texte = ""
                texte += f"Dossier vide: {name}\n"
                texte += f"Taille: {size}\n"
                texte += f"ID: {id}\n"
                texte += f"Chemin: {path}\n"

                self.ajouter_layout(texte, None, None, id)

        else:
            # Aucun fichier vide trouvé
            logger.warning("Aucun fichier vide trouvé")
            texte = "Aucun fichier vide n'a été trouvé !\n"
            self.ajouter_layout(texte, None, None, None)

    def useless(self):
        logger.info("Méthode useless en usage")

        self.stop_existing_thread('thread_useless')

        modes_disponibles = [
            "Fichiers temporaires (extensions)",
            "Fichiers très petits (taille < xKB)", 
            "Fichiers anciens (> x ans)",
            "Fichiers temporaires et très petits",
            "Tous les modes combinés"
        ]
        
        # Pop-up pour demander le seuil
        mode, ok = InputDialog.getItem(
            self,
            "Mode de détection",
            "Choisissez le type de fichiers inutiles à détecter :",
            modes_disponibles,
            0,  # Index par défaut (premier élément)
            False  # Non éditable
        )
        
        if not ok:  # Utilisateur a annulé
            return
        
        def max_size_fct():
            max_size, ok = InputDialog.getInt(
                self,
                "Taille maximale",
                "Choisissez la taille en bytes en dessous de laquelle vous voulez détecter les fichiers :",
                1000,  # Valeur par défaut
                1,
                999999999
            )
            
            return max_size if ok else 1000

        def years_fct():
            years, ok = InputDialog.getInt(
                self, 
                "Année", 
                "Choisissez le nombre d'année à partir de laquelle vous voulez détecter les fichiers :", 
                4,  # Valeur par défaut
                0, 
                20
            )

            return years if ok else 4
        
        mode_choisi = None
        max_size = 1000
        years = 4

        if mode == modes_disponibles[0]:
            mode_choisi = "ext"

        elif mode == modes_disponibles[1]:
            mode_choisi = "siz"

            max_size = max_size_fct()

        elif mode == modes_disponibles[2]:
            mode_choisi = "old"

            years = years_fct()

        elif mode == modes_disponibles[3]:
            mode_choisi = "two"

            max_size = max_size_fct()

        elif mode == modes_disponibles[4]:
            mode_choisi = "all"

            max_size = max_size_fct()
            years = years_fct()

        else:
            return None
        
        logger.debug(f"L'utilisateur a choisi {mode_choisi}")

        self.begin()
        self.current_number = 0
        self.current_displayed_doublon = 0
        self.doublons_liste =  []

        # Nettoyage de la liste précédente
        while self.vbox.count():
            child = self.vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Configuration et lancement du thread de détection
        self.thread_useless = QThread()
        self.worker_useless = ThreadUseless(mode_choisi, max_size, years)
        self.worker_useless.moveToThread(self.thread_useless)

        # Connexions des signaux
        self.worker_useless.progression.connect(self.ajouter_layout)
        self.thread_useless.started.connect(self.worker_useless.run)
        self.worker_useless.finished.connect(self.thread_useless.quit)
        self.worker_useless.finished.connect(self.worker_useless.deleteLater)
        self.thread_useless.finished.connect(self.thread_useless.deleteLater)
        self.thread_useless.finished.connect(self.end)

        self.thread_useless.start()

    def ajouter_layout(self, data, ids, chemins, single_id = None):
        """
        Ajoute un doublon trouvé à la liste d'affichage scrollable.
        
        Cette méthode est appelée via signal à chaque fois qu'un thread
        de détection trouve une paire de doublons. Elle crée un widget
        d'affichage avec les détails du doublon et un bouton de prévisualisation.
        
        Args:
            data (str): Texte descriptif du doublon
            ids (tuple): Tuple (id1, id2) des fichiers OneDrive
            chemins (tuple): Tuple (chemin1, chemin2) des fichiers
        """
        # Assignation d'un numéro unique au doublon
        self.current_number += 1
        doublon_number = self.current_number

        if ids and chemins:
            id1, id2 = ids
            chemin1, chemin2 = chemins

            logger.debug(f"Ajout doublon #{doublon_number}: {id1} <-> {id2}")

            # Stockage du doublon pour navigation ultérieure
            self.doublons_liste.append({
                'id1': id1,
                'id2': id2,
                'chemin1': chemin1,
                'chemin2': chemin2,
                'number': doublon_number
            })
            
        # Création du widget conteneur pour ce doublon
        container = QWidget()
        container.setStyleSheet(style.cssDoublonContainer)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(8, 5, 8, 5)
        main_layout.setSpacing(5)

        # Texte descriptif du doublon
        label = Text(data)
        label.setStyleSheet(style.cssTexte)
        label.setWordWrap(True)

        text = label.text()
        
        # Si ce n'est pas le message "Aucun doublon", on ajoute les contrôles
        if "Aucun" not in text:
            # Layout horizontal pour le numéro + texte + bouton loupe (si applicable)
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(5)

            # Numéro du doublon (pour navigation visuelle)
            chiffre = Text(str(doublon_number))
            chiffre.setStyleSheet(style.cssChiffre)
            chiffre.setFixedWidth(80)
            chiffre.setAlignment(Qt.AlignCenter)
            container.chiffre_widget = chiffre  # Référence pour le changement de couleur
            
            top_layout.addWidget(chiffre)
            top_layout.addWidget(label)

            if "Dossier vide" not in text:
                # Bouton loupe pour prévisualiser ce doublon
                bouton_loupe = Bouton("🔎", lambda: self.prev_comparaison(id1, id2, chemin1, chemin2, doublon_number), True, 32, 32, False, style.cssLoupe)
                top_layout.addWidget(bouton_loupe)
            
                # Ajouter seulement le layout horizontal
                main_layout.addLayout(top_layout)
            
            # Si c'est un empty_folder
            elif "Dossier vide" in text:
                # Ajouter le layout horizontal (numéro + texte)
                main_layout.addLayout(top_layout)
                
                def suppression(single_id):
                    bouton_supprimer.setStyleSheet(style.cssBoutonErreur)

                    self.suppr(single_id, None)
                    
                    QTimer.singleShot(3500, reset)

                def reset():
                    bouton_supprimer.setStyleSheet(style.cssBouton)

                # Ajouter le bouton supprimer SOUS le texte
                bouton_supprimer = Bouton("Supprimer", lambda: suppression(single_id))

                # Layout pour centrer le bouton
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                button_layout.addWidget(bouton_supprimer)
                button_layout.addStretch()
                
                main_layout.addLayout(button_layout)

        else:
            # Cas "Aucun doublon trouvé"
            main_layout.addWidget(label)

        # Ajout à la liste scrollable
        self.vbox.addWidget(container)

    def prev_comparaison(self, id1, id2, chemin1, chemin2, doublon_number):
        """
        Lance la génération de prévisualisations pour comparer deux doublons.
        
        Cette méthode:
        1. Met à jour l'indicateur de doublon actuellement affiché
        2. Désactive temporairement l'interface
        3. Lance un thread ThreadPreview pour télécharger les images
        4. Met à jour les couleurs des numéros de doublons dans la liste
        
        Args:
            id1, id2 (str): IDs OneDrive des deux fichiers à comparer
            chemin1, chemin2 (str): Chemins complets des fichiers
            doublon_number (int): Numéro du doublon dans la liste
        """
        self.stop_existing_thread('thread_prev')

        # Marquage du doublon actuellement visualisé
        self.current_displayed_doublon = doublon_number

        # Désactivation temporaire de l'interface
        self.begin()

        # Configuration et lancement du thread de prévisualisation
        self.thread_prev = QThread()
        self.worker_prev = ThreadPreview(self.token, id1, id2, chemin1, chemin2)
        self.worker_prev.moveToThread(self.thread_prev)

        # Connexions des signaux
        self.worker_prev.image.connect(self.prev_add)
        self.thread_prev.started.connect(self.worker_prev.preview)
        self.worker_prev.finished.connect(self.thread_prev.quit)
        self.worker_prev.finished.connect(self.worker_prev.deleteLater)
        self.thread_prev.finished.connect(self.thread_prev.deleteLater)
        self.thread_prev.finished.connect(lambda: self.end(True, id1, id2, doublon_number))
        
        # Mise à jour visuelle de la liste (surbrillance du doublon actuel)
        self.refresh_chiffre_colors()

        self.thread_prev.start()

    def prev_add(self, imgs_and_paths):
        """
        Affiche les images de prévisualisation dans l'interface.
        
        Cette méthode est appelée quand le thread ThreadPreview a terminé
        le téléchargement des deux images à comparer.
        
        Args:
            imgs_and_paths (tuple): (QPixmap1, QPixmap2, chemin1, chemin2)
        """
        img1, img2, path1, path2 = imgs_and_paths
        
        # Affichage des images dans les zones dédiées
        self.label_image_doublons_1.set_image(img1)
        self.label_image_doublons_2.set_image(img2)
        
        # Affichage des chemins sous les images
        self.label_chemin_1.setText(path1 if path1 else "")
        self.label_chemin_2.setText(path2 if path2 else "")
        
        # Mise à jour immédiate de l'affichage
        QApplication.processEvents()

    def refresh_chiffre_colors(self):
        """
        Met à jour les couleurs des numéros de doublons dans la liste.
        
        Met en surbrillance le doublon actuellement affiché et remet
        les autres en couleur normale.
        """
        for i in range(self.vbox.count()):
            container = self.vbox.itemAt(i).widget()

            # Vérification que le container a un widget numéro
            if hasattr(container, 'chiffre_widget'):
                doublon_num = int(container.chiffre_widget.text())

                # Application du style actif ou normal selon l'état
                if doublon_num == self.current_displayed_doublon:
                    container.chiffre_widget.setStyleSheet(style.cssChiffreActive)
                    
                else:
                    container.chiffre_widget.setStyleSheet(style.cssChiffre)

    def begin(self):
        """
        Désactive tous les contrôles pendant un traitement en cours.
        
        Cette méthode est appelée au début de chaque opération longue
        (détection, prévisualisation) pour éviter les interactions utilisateur
        pendant le traitement.
        """
        # Désactivation des boutons de détection
        self.bouton_hash_nom_taille.set_button(False)
        self.bouton_visuel.set_button(False)
        self.bouton_empty_folder.set_button(False)
        self.bouton_inutile.set_button(False)
        self.bouton_retour.set_button(False)
        
        # Désactivation des boutons de gestion des doublons
        self.bouton_suppression1.set_button(False)
        self.bouton_suppression2.set_button(False)
        self.bouton_precedent.set_button(False)
        self.bouton_suivant.set_button(False)

        # Remise à zéro de l'affichage des images
        self.label_image_doublons_1.pixmap_default()
        self.label_image_doublons_2.pixmap_default()
        
        # Effacement des chemins affichés
        self.label_chemin_1.setText("")
        self.label_chemin_2.setText("")

    def end(self, prev = False, id1 = None, id2 = None, doublon_number = 0):
        """
        Réactive les contrôles à la fin d'un traitement.
        
        Args:
            prev (bool): True si on affiche une prévisualisation, False sinon
            id1, id2 (str): IDs des fichiers en cours de prévisualisation
            doublon_number (int): Numéro du doublon affiché
        """
        # Réactivation des boutons principaux
        if self.etat_bouton_hash_nom_taille:
            self.bouton_hash_nom_taille.set_button(True)

        if self.etat_bouton_visuel:
            self.bouton_visuel.set_button(True)

        if self.etat_bouton_empty_folder:
            self.bouton_empty_folder.set_button(True)

        if self.etat_bouton_useless:
            self.bouton_inutile.set_button(True)
            
        self.bouton_retour.set_button(True)

        # Si on affiche une prévisualisation, activer les contrôles spécifiques
        if prev:
            # Activation des boutons de navigation selon la position
            if doublon_number > 1:
                self.bouton_precedent.set_button(True)
                
            if doublon_number < len(self.doublons_liste):
                self.bouton_suivant.set_button(True)

            # === RECONNEXION DYNAMIQUE DES SIGNAUX ===
            # Les boutons de suppression et navigation doivent être reconnectés
            # à chaque nouvelle prévisualisation car les IDs changent
            
            # Déconnexion des anciens signaux (évite les connexions multiples)
            try:
                self.bouton_suppression1.clicked.disconnect()
            except TypeError:
                logger.debug("Pas de connexion précédente pour bouton_suppression1")
                pass 

            try:
                self.bouton_suppression2.clicked.disconnect()
            except TypeError:
                logger.debug("Pas de connexion précédente pour bouton_suppression2")
                pass

            try:
                self.bouton_precedent.clicked.disconnect()
            except TypeError:
                logger.debug("Pas de connexion précédente pour bouton_precedent")
                pass

            try:
                self.bouton_suivant.clicked.disconnect()
            except TypeError:
                logger.debug("Pas de connexion précédente pour bouton_suivant")
                pass

            # Reconnexion avec les nouveaux paramètres                
            if id1:
                self.bouton_suppression1.set_button(True)
                self.bouton_suppression1.clicked.connect(lambda: self.suppr_verif(id1, 1))

            if id2:
                self.bouton_suppression2.set_button(True)
                self.bouton_suppression2.clicked.connect(lambda: self.suppr_verif(id2, 2))

            if not id1 or not id2:
                self.is_suppr = True

            self.bouton_precedent.clicked.connect(lambda: self.precedent(doublon_number))
            self.bouton_suivant.clicked.connect(lambda: self.suivant(doublon_number))

    def suppr_verif(self, id:str, number:int):
        if not self.is_suppr:
            self.suppr(id, number)
            self.is_suppr = True

        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirmation de suppression")
            msg_box.setText("Êtes-vous sûr de vouloir supprimer ce fichier ?")
            msg_box.setInformativeText("Cette action est irréversible.")
            msg_box.setIcon(QMessageBox.Question)

            # Boutons Oui et Non
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)  # Bouton par défaut
            
            # Texte des boutons en français
            msg_box.button(QMessageBox.Yes).setText("Oui")
            msg_box.button(QMessageBox.No).setText("Non")
            
            # Affichage et récupération de la réponse
            response = msg_box.exec_()
            
            if response == QMessageBox.Yes:
                self.suppr(id, number)
                self.is_suppr = False

    def suppr(self, id:str, number:int):
        """
        Supprime un fichier depuis OneDrive via l'API Microsoft Graph.
        
        Args:
            id (str): ID OneDrive du fichier à supprimer
            number (int): Numéro de l'image (1 ou 2) pour l'affichage
        """
        logger.info(f"Suppression demandée pour l'image {number} (ID: {id})")
        
        # Appel API de suppression
        endpoint = f"me/drive/items/{id}"
        response = call_web_api(endpoint, self.token, None, "delete")
        logger.debug(f"Réponse API suppression: {response}")

        # Traitement de la réponse
        if response == 204:
            # Suppression réussie
            logger.info(f"Image {number} supprimée avec succès")
            if number == 1:
                self.label_chemin_1.setText("Image supprimé !")
                self.label_image_doublons_1.pixmap_default()

            elif number == 2:
                self.label_chemin_2.setText("Image supprimé !")
                self.label_image_doublons_2.pixmap_default()

        elif response == 404:
            # Fichier déjà supprimé ou introuvable
            logger.warning(f"Image {number} déjà supprimée (404)\n{traceback.format_exc()}")
            if number == 1:
                self.label_chemin_1.setText("Image déjà supprimé !")
                self.label_image_doublons_1.pixmap_default()

            elif number == 2:
                self.label_chemin_2.setText("Image déjà supprimé !")
                self.label_image_doublons_2.pixmap_default()
        else:
            # Autre erreur
            logger.error(f"Erreur lors de la suppression de l'image {number}: code {response}\n{traceback.format_exc()}")

    def precedent(self, doublon_number):
        """
        Navigue vers le doublon précédent dans la liste.
        
        Args:
            doublon_number (int): Numéro du doublon actuellement affiché
        """
        logger.debug(f"Navigation vers doublon précédent - actuel: {doublon_number}")
        
        if doublon_number > 1:
            # Récupération des informations du doublon précédent
            next_doublon = self.doublons_liste[doublon_number - 2]  # -2 car index 0-based
            id1 = next_doublon['id1']
            id2 = next_doublon['id2']
            chemin1 = next_doublon['chemin1']
            chemin2 = next_doublon['chemin2']
            logger.debug(f"Doublon précédent trouvé: #{doublon_number - 1}")

            # Lancement de la prévisualisation du doublon précédent
            self.prev_comparaison(id1, id2, chemin1, chemin2, doublon_number - 1)

    def suivant(self, doublon_number):
        """
        Navigue vers le doublon suivant dans la liste.
        
        Args:
            doublon_number (int): Numéro du doublon actuellement affiché
        """
        logger.debug(f"Navigation vers doublon suivant - actuel: {doublon_number}")
        
        if doublon_number < len(self.doublons_liste):
            # Récupération des informations du doublon suivant
            next_doublon = self.doublons_liste[doublon_number]  # doublon_number car index 0-based
            id1 = next_doublon['id1']
            id2 = next_doublon['id2']
            chemin1 = next_doublon['chemin1']
            chemin2 = next_doublon['chemin2']
            logger.debug(f"Doublon suivant trouvé: #{doublon_number + 1}")

            # Lancement de la prévisualisation du doublon suivant
            self.prev_comparaison(id1, id2, chemin1, chemin2, doublon_number + 1)

    def stop_existing_thread(self, thread_attr_name):
        """
        Arrête proprement un thread existant s'il est encore en cours.
        
        Args:
            thread_attr_name (str): Nom de l'attribut contenant le thread
        """
        if hasattr(self, thread_attr_name):
            thread = getattr(self, thread_attr_name)
            if thread is not None:
                try:
                    if thread.isRunning():
                        logger.info(f"Arrêt du thread {thread_attr_name} en cours")
                        thread.quit()
                        thread.wait(3000)  # Attend max 3 secondes

                    try:
                        if thread.isRunning():
                            logger.warning(f"Thread {thread_attr_name} ne s'arrête pas, terminaison forcée")
                            thread.terminate()
                            thread.wait()
                    except RuntimeError:
                        # Thread déjà détruit pendant wait()
                        logger.debug(f"Thread {thread_attr_name} détruit pendant l'arrêt")
                        
                except RuntimeError as e:
                    # L'objet C++ a été détruit
                    logger.debug(f"Thread {thread_attr_name} déjà détruit: {e}")
                
            # Nettoyage de la référence dans tous les cas
            setattr(self, thread_attr_name, None)

    def retour_accueil(self):
        """Retourne à la page d'accueil de l'application."""
        logger.info("Retour à l'accueil depuis la page des doublons")
        if self.parent_interface:
            self.parent_interface.stack.setCurrentIndex(0)