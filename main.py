# main.py
"""
OneDrive Duplicate Finder - Interface principale

Ce module contient l'interface utilisateur principale de l'application OneDrive Duplicate Finder.
Il gère l'authentification Microsoft, le parcours des photos/vidéos OneDrive, la détection de doublons
et l'interface graphique avec PyQt5.

Auteur: Victor Defauchy
Date: 2025
"""

# ===============
# === IMPORTS ===
# ===============
# Threading et interface web
import threading
import webbrowser

# Interface graphique PyQt5
from PyQt5.QtWidgets import QApplication, QShortcut, QWidget, QVBoxLayout, QGraphicsOpacityEffect, QStackedWidget, QPushButton
from PyQt5.QtCore import Qt, QRect, QTimer, QSize
from PyQt5.QtGui import QIcon, QKeySequence

# Système et utilitaires
import sys
import os
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
from fonctions.logger import *
from fonctions.token_manager import *
from fonctions.server import *
from fonctions.sql import *
from fonctions.threads import *
from fonctions.doublons import *
from fonctions.compte_photos import *

# TO DO
# Ajouter une fonction pour supprimer toute la liste d'un coup avec fenêtre pop-up de vérification
# Redéployer une nouvelle version

# =================
# === INTERFACE ===
# =================
class Interface(QWidget):
    """
    Interface principale de l'application OneDrive Duplicate Finder.
    
    Cette classe est le point d'entrée principal de l'interface utilisateur.
    
    Attributes:
        token (str): Token d'authentification Microsoft Graph API
        stack (QStackedWidget): Gestionnaire de pages
        page_accueil (QWidget): Page principale de l'application
        page_dedoublons (Doublons): Page de gestion des doublons
        sidebar_visible (bool): État d'affichage de la sidebar
    """
    def __init__(self):
        """
        Initialise l'interface principale de l'application.
        """
        super().__init__()

        logger.info("Initialisation de l'interface principale")
        
        # Style général de la fenêtre
        self.setStyleSheet(f"background-color: {style.couleur_fond};")
        
        # Génération du token d'authentification OAuth2
        self.token = self.authenticate()
        if self.token:
            logger.info("Authentification réussie")

        else:
            logger.warning(f"Échec de l'authentification\n{traceback.format_exc()}")

        # Définition du système de pages empilées
        self.stack = QStackedWidget(self)
        self.page_accueil = QWidget()                             # Page 0: Accueil
        self.page_compte_photos = ComptePhotos(self.token, self)  # Page 1 : Compte Photos
        self.page_dedoublons = Doublons(self.token, self)         # Page 2: Gestion doublons
        self.stack.addWidget(self.page_accueil)
        self.stack.addWidget(self.page_compte_photos)
        self.stack.addWidget(self.page_dedoublons)

        # Eléments de la page
            # Gestion des paramètres
        self.sidebar_visible = False
        self.overlay()

            # Bouton Parametre
        self.bouton_parametre = QPushButton(self)
        self.bouton_parametre.setGeometry(self.width() - 42, 10, 32, 32)
        self.bouton_parametre.setIconSize(QSize(32, 32))
        self.bouton_parametre.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "content", "settings_logo.png")))
        self.bouton_parametre.setCursor(Qt.PointingHandCursor)
        self.bouton_parametre.setFlat(True)
        self.bouton_parametre.clicked.connect(self.toggle_sidebar)

            # Texte
        titre = Text("OneDrive Duplicate Finder", style.cssTitre)

            # Fonction complémentaire
        def trier_les_photos():
            self.stack.setCurrentWidget(self.page_dedoublons)
            self.page_dedoublons.verif_boutons()
            self.page_dedoublons.is_suppr = False

            # Boutons
        self.bouton_compte_photos = Bouton("Compter les photos", lambda: self.stack.setCurrentWidget(self.page_compte_photos))
        self.bouton_dedoublonner = Bouton("Trier les photos", trier_les_photos)
        self.bouton_quitter = Bouton("Quitter", self.quitter)

        layout = QVBoxLayout(self.page_accueil)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        layout.addSpacing(100)
        layout.addWidget(titre, 0, Qt.AlignCenter)
        layout.addSpacing(200)
        layout.addWidget(self.bouton_compte_photos, 0, Qt.AlignCenter)
        layout.addWidget(self.bouton_dedoublonner, 0, Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.bouton_quitter, 0, Qt.AlignCenter)
        layout.addSpacing(100)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stack)

        self.setLayout(layout_principal)

        self.bouton_parametre.raise_()
        
        self.show()

        # Gestion des shortscut
        self.shortcut_escape = QShortcut(QKeySequence("Escape"), self)
        self.shortcut_escape.activated.connect(lambda: self.escape())

        self.shortcut_doublons = QShortcut(QKeySequence("d"), self)
        self.shortcut_doublons.activated.connect(lambda: trier_les_photos())

        self.shortcut_compte = QShortcut(QKeySequence("c"), self)
        self.shortcut_compte.activated.connect(lambda: self.stack.setCurrentWidget(self.page_compte_photos))

        self.shortcut_parametres = QShortcut(QKeySequence("p"), self)
        self.shortcut_parametres.activated.connect(lambda: self.toggle_sidebar())

    def escape(self):
        if self.stack.currentWidget() is not self.page_accueil:
            self.stack.setCurrentWidget(self.page_accueil)
        
        else:
            self.quitter()

    def overlay(self):
        """
        Crée la sidebar de paramètres avec overlay et animations.
        
        Cette méthode configure:
        1. Un arrière-plan semi-transparent (overlay) pour obscurcir l'interface
        2. Une sidebar coulissante depuis la droite avec les paramètres
        3. Les animations d'apparition/disparition
        4. Le contenu de la sidebar (informations utilisateur, boutons d'action)
        """
        
        # Widget d'arrière-plan semi-transparent
        self.background = QWidget(self)
        self.background.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.background.setGeometry(self.rect())
        
        # Effet d'opacité pour les animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.0)  # Initialement invisible
        self.background.setGraphicsEffect(self.opacity_effect)
        
        # Clic sur l'overlay ferme la sidebar
        self.background.mousePressEvent = lambda event: self.toggle_sidebar()
        
        # Widget sidebar coulissante
        self.sidebar = QWidget(self)
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet(f"background-color: {style.couleur_fond};")
        # Position initiale: hors écran à droite
        self.sidebar.setGeometry(self.width(), 0, 300, self.height())
        
        sidebar_layout = QVBoxLayout()

        # Titre de la section paramètres
        titre_sidebar = Text("Paramètres", style.cssParametreTitre)
        
        # Informations de crédits et présentation
        credit = Text("OneDrive Duplicate Finder\n" \
        "Outil de recherches de doublons \nde photos et vidéos sur OneDrive\n\n" \
        "Projet réalisé par Victor Defauchy\n\n" \
        "duplicatefinder.fr\n")
        credit.setStyleSheet(style.cssUser)

        # Informations de l'utilisateur connecté
        text_user = self.affiche_user()
        self.user = Text(text_user, style.cssUser)

        # Boutons d'action de la sidebar
        self.bouton_reconnect = Bouton("Se reconnecter", self.reconnect)
        self.bouton_site = Bouton("Vers le site", lambda: webbrowser.open("duplicatefinder.fr"))
        self.bouton_quitter_overlay = Bouton("Quitter", self.quitter)
        
        # Configuration des espacements et marges
        sidebar_layout.setSpacing(50)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Ajout des éléments avec espacements
        sidebar_layout.addSpacing(50)                                              
        sidebar_layout.addWidget(titre_sidebar, alignment = Qt.AlignCenter)       
        sidebar_layout.addWidget(self.user, alignment = Qt.AlignCenter)           
        sidebar_layout.addWidget(self.bouton_reconnect, alignment = Qt.AlignCenter)
        sidebar_layout.addSpacing(50)                                             
        sidebar_layout.addWidget(self.bouton_site, alignment = Qt.AlignCenter)        
        sidebar_layout.addWidget(credit, alignment = Qt.AlignCenter)              
        sidebar_layout.addStretch()                                               
        sidebar_layout.addWidget(self.bouton_quitter_overlay, alignment = Qt.AlignCenter)      
        sidebar_layout.addSpacing(50)                                             

        self.sidebar.setLayout(sidebar_layout)
        
        # Les éléments de la sidebar doivent être au-dessus du contenu principal
        self.background.raise_()  # Overlay au-dessus du contenu
        self.sidebar.raise_()     # Sidebar au-dessus de l'overlay

        # État initial: éléments cachés
        self.background.hide()
        self.sidebar.hide()

    def toggle_sidebar(self):
        """
        Affiche ou masque la sidebar avec animations fluides.
        
        Cette méthode gère l'état d'affichage de la sidebar en alternant entre
        les modes ouvert/fermé avec des animations synchronisées:
        """
        if not self.sidebar_visible:
            
            # Mise au premier plan des éléments
            self.background.raise_()
            self.sidebar.raise_()

            # Affichage des éléments
            self.background.show()
            self.sidebar.show()

            # Animations d'apparition synchronisées
            # Overlay: fondu entrant (opacité 0→1)
            self.animation_background = Animation(self.opacity_effect, b"opacity", 300, 0.0, 1.0)
            # Sidebar: glissement depuis la droite
            self.animation_sidebar = Animation(self.sidebar, b"geometry", 300, QRect(self.width(), 0, 300, self.height()), QRect(self.width() - 300, 0, 300, self.height()))
            # Bouton: déplacement vers la gauche pour rester visible
            self.animation_bouton = Animation(self.bouton_parametre, b"geometry", 300, QRect(self.width() - 42, 10, 32, 32), QRect(self.width() - 342, 10, 32, 32))
            
            # Actualisation des informations utilisateur si erreur précédente
            if self.user.text() == "Erreur lors de la reconnexion":
                self.affiche_user()

        else:
            
            # Animations de disparition synchronisées
            # Overlay: fondu sortant (opacité 1→0)
            self.animation_background = Animation(self.opacity_effect, b"opacity", 300, 1.0, 0.0)
            # Sidebar: glissement vers la droite (hors écran)
            self.animation_sidebar = Animation(self.sidebar, b"geometry", 300, QRect(self.width() - 300, 0, 300, self.height()), QRect(self.width(), 0, 300, self.height()))
            # Bouton: retour à sa position initiale
            self.animation_bouton = Animation(self.bouton_parametre, b"geometry", 300, QRect(self.width() - 342, 10, 32, 32), QRect(self.width() - 42, 10, 32, 32))

            # Masquage des éléments à la fin des animations
            self.animation_background.finished.connect(self.background.hide)
            self.animation_sidebar.finished.connect(self.sidebar.hide)

        # Inversion de l'état d'affichage
        self.sidebar_visible = not self.sidebar_visible

    def resizeEvent(self, event):
        """
        Gestionnaire d'événement de redimensionnement de la fenêtre.
        
        Cette méthode est automatiquement appelée lorsque l'utilisateur redimensionne
        la fenêtre principale. Elle ajuste la position et taille des éléments
        d'interface qui ne sont pas gérés par les layouts automatiques:
        
        - Overlay d'arrière-plan (doit couvrir toute la fenêtre)
        - Position de la sidebar (maintien à droite de l'écran)
        - Position du bouton paramètres (coin supérieur droit)
        
        Args:
            event (QResizeEvent): Événement de redimensionnement Qt
        """
        # Appel du gestionnaire parent pour le comportement standard
        super().resizeEvent(event)
        
        # Ajustement de l'overlay pour couvrir toute la nouvelle taille
        self.background.setGeometry(self.rect())
        
        # Repositionnement de la sidebar selon son état (visible/masquée)
        sidebar_x = self.width() - 300 if self.sidebar_visible else self.width()
        self.sidebar.setGeometry(sidebar_x, 0, 300, self.height())
        
        # Repositionnement du bouton paramètres dans le coin supérieur droit
        self.bouton_parametre.setGeometry(self.width() - 42, 10, 32, 32)

    def affiche_user(self):
        """
        Récupère et formate les informations de l'utilisateur connecté.
        
        Cette méthode interroge l'API Microsoft Graph pour obtenir les informations
        du compte utilisateur actuellement authentifié via le token OAuth2.
        
        Informations récupérées:
        - Nom d'affichage (displayName)
        - ID utilisateur unique (id)  
        - Adresse email (mail)
        
        Returns:
            str: Texte formaté contenant les informations utilisateur,
                 ou message d'erreur en cas de problème
        
        Gestion d'erreurs:
        - Token manquant: Message de reconnexion
        - Échec API: Message "Aucun utilisateur trouvé"
        """
        logger.info("Fonction afficher utilisateur cliqué")

        # Vérification de la présence du token d'authentification
        if not self.token:
            logger.warning(f"Token manquant - impossible d'afficher les informations utilisateur\n{traceback.format_exc()}")
            return "Token manquant - reconnectez-vous"

        # Construction du texte de présentation
        texte = "Informations sur le compte connecté :\n\n"
        
        # Configuration de l'appel API Microsoft Graph
        endpoint = "me"  # Endpoint pour les informations du compte actuel
        select = ['displayName', 'id', 'mail']  # Champs spécifiques à récupérer
    
        # Appel à l'API Microsoft Graph
        user_data = call_web_api(endpoint, self.token, select)

        logger.debug(f"Données utilisateur reçues: {user_data is not None}")

        if user_data:
            # Formatage des informations utilisateur
            texte += f"Nom : {user_data.get('displayName', 'N/A')}\n"
            texte += f"User ID : {user_data.get('id', 'N/A')}\n"
            texte += f"Email : {user_data.get('mail', 'N/A')}\n"

            logger.info("Utilisateur trouvé et référencé avec succès")
            
        else:
            # Gestion des erreurs d'API
            logger.warning(f"Aucun utilisateur trouvé ou erreur lors de la requête.\n{traceback.format_exc()}")
            return "Aucun utilisateur trouvé"

        return texte

    def authenticate(self):
        """
        Gère le processus d'authentification Microsoft OAuth2.
        
        Cette méthode implémente le flux d'authentification OAuth2 pour l'API Microsoft Graph:
        
        1. Vérification d'un token existant et valide
        2. Si aucun token valide, lancement du processus d'authentification:
           - Démarrage d'un serveur local pour recevoir le code d'autorisation
           - Ouverture du navigateur avec l'URL d'authentification Microsoft
           - Attente du code d'autorisation depuis Microsoft
           - Échange du code contre un token d'accès
        
        Returns:
            str: Token d'accès Microsoft Graph API valide, ou None en cas d'échec
            
        Processus d'authentification:
        - L'utilisateur est redirigé vers Microsoft pour s'authentifier
        - Microsoft renvoie un code d'autorisation au serveur local
        - Le code est échangé contre un token d'accès JWT
        - Le token est stocké pour les utilisations futures
        """
        
        # Tentative de récupération d'un token stocké et valide
        access_token = get_access_token()

        if access_token:
            logger.info("Token valide trouvé.")
            return access_token
        
        logger.warning("Aucune session valide. Lancement de l'authentification...")

        # Démarrage du serveur local pour recevoir le callback Microsoft
        server_thread = threading.Thread(target = start_server, daemon = True)
        server_thread.start()

        # Construction de l'URL d'authentification Microsoft
        auth_url = build_auth_url()
        
        # Ouverture du navigateur pour l'authentification utilisateur
        webbrowser.open(auth_url)

        # Attente du code d'autorisation depuis Microsoft
        code = wait_for_code()
        
        # Échange du code contre un token d'accès
        access_token = acquire_token_by_code(code)

        logger.info("Authentification réussie.")
        return access_token
    
    def reconnect(self):
        """
        Force une nouvelle authentification Microsoft.
        
        Cette méthode:
        1. Supprime le token d'accès existant (même s'il est encore valide)
        2. Lance un nouveau processus d'authentification complet
        3. Met à jour l'interface utilisateur avec les nouvelles informations
        4. Fournit un retour visuel à l'utilisateur pendant le processus
        """
        logger.info("Fonction reconnection cliqué")
        
        # Modification visuelle du bouton pour indiquer le processus en cours
        self.bouton_reconnect.setText("Reconnection...")
        self.bouton_reconnect.setStyleSheet(style.cssBoutonErreur)
        
        # Suppression du token existant pour forcer une nouvelle authentification
        delete_token()
        
        # Lancement du processus d'authentification complet
        self.token = self.authenticate()
        
        if self.token:
            logger.info("Nouveau token généré avec succès")
            
            # Mise à jour des informations utilisateur dans la sidebar
            self.user.setText(self.affiche_user())

        else:
            logger.error(f"Échec de génération du nouveau token\n{traceback.format_exc()}")
            
            # Affichage d'un message d'erreur à l'utilisateur
            self.user.setText("Erreur lors de la reconnexion")
        
        # Fonction de restauration différée pour laisser le temps à l'utilisateur de voir le résultat
        def reset():
            self.bouton_reconnect.setText("Se reconnecter")
            self.bouton_reconnect.setStyleSheet(style.cssBouton)

        # Restauration automatique après 3.5 secondes
        QTimer.singleShot(3500, reset)

    def quitter(self):
        """
        Ferme proprement l'application.
        """
        logger.info("Fonction quitter cliqué")

        # Changement des états
        self.bouton_compte_photos.set_button(False)
        self.bouton_dedoublonner.set_button(False)
        self.bouton_quitter.set_button(False)
        self.bouton_reconnect.set_button(False)
        self.bouton_site.set_button(False)
        self.bouton_quitter_overlay.set_button(False)

        # Changement des couleurs des boutons quitter en rouge
        self.bouton_quitter.setStyleSheet(style.cssBoutonErreur)
        self.bouton_quitter_overlay.setStyleSheet(style.cssBoutonErreur)

        # Attente de 1 seconde avant la fermeture forcée
        QTimer.singleShot(1000, lambda: os._exit(0))

# ============
# === MAIN ===
# ============
if __name__ == "__main__":
    """
    Point d'entrée principal de l'application OneDrive Duplicate Finder.
    
    Processus de démarrage:
    - Création du logger pour tracer l'activité de l'application
    - Initialisation de QApplication (gestionnaire d'interface Qt)
    - Création de l'interface principale (authentification + GUI)
    - Configuration de la fenêtre (titre, mode maximisé)
    - Entrée dans la boucle d'événements Qt jusqu'à fermeture
    """
    # Configuration du système de logging
    logger = connecteLogger(__name__)

    logger.info("\n=== LOGS OneDrive Duplicate Finder ===\n\n")
    logger.info("Application OneDrive Duplicate Finder démarrée")
    logger.debug("Création de l'application Qt")
    app = QApplication(sys.argv)

    logger.debug("Initialisation de l'interface principale")
    window = Interface()
    
    window.setWindowTitle("OneDrive Duplicate Finder")
    logger.info("Affichage de la fenêtre principale en mode maximisé")
    window.showFullScreen()

    logger.info("Entrée dans la boucle principale de l'application")
    sys.exit(app.exec_())