# comptes_photos.py

# ===============
# === IMPORTS ===
# ===============

# Interface graphique PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap

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
from fonctions.threads import ParcoursPhotos

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

class ComptePhotos(QWidget):
    def __init__(self, token, parent=None):
        super().__init__(parent)
        logger.info("Initialisation de la classe ComptePhotos")
        self.token = token
        self.parent_interface = parent

        self.type = ["Images", "Videos", "Documents", "Empty Folder"]

            # Textes
        titre = Text("Compte des Photos", style.cssTitre)
        texte_type = Text("Détecter :")

            # Boutons
        self.bouton_compte = Bouton("Compter mes photos", self.parcours_photos)
        self.bouton_previsualisation = Bouton("Prévisualisation désactivé", self.prev_turn, True, 350, 70, True)
        self.bouton_pause = Bouton("Pause", self.pause, False)
        self.bouton_continuer = Bouton("Continuer", self.continuer, False)
        self.bouton_stop = Bouton("Stop", self.stop, False)
        self.bouton_retour_accueil = Bouton("Retour à l'accueil", self.retour_accueil)
        self.bouton_type_image = Bouton("Images", lambda: self.type_change(self.bouton_type_image), True, 250, 70, False, style.cssBoutonAcheve)
        self.bouton_type_video = Bouton("Vidéos", lambda: self.type_change(self.bouton_type_video), True, 250, 70, False, style.cssBoutonAcheve)
        self.bouton_type_documents = Bouton("Documents", lambda: self.type_change(self.bouton_type_documents), True, 250, 70, False, style.cssBoutonAcheve)
        self.bouton_type_empty_folder = Bouton("Dossiers vides", lambda: self.type_change(self.bouton_type_empty_folder), True, 250, 70, False, style.cssBoutonAcheve)

            # Label image
        self.label_image = LabelImage(600, 400)

            # Zone texte
        self.affichage = TextEdit("Comptez toutes vos photos")

        # Définitions des layouts
            # Layout principal de la fenêtre
        layout = QVBoxLayout(self)
        
            # Layout pour la page d'accueil
        layout_accueil = QVBoxLayout()
        spinbox_row = QHBoxLayout()
        layout_top_row = QHBoxLayout()
        layout_right_buttons = QVBoxLayout()
        layout_pixmap_buttons = QGridLayout()

        # Définitions des containers
        top_row_container = QWidget()
        top_row_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        spinbox_container = QWidget()
        spinbox_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        right_buttons_container = QWidget()
        right_buttons_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pixmap_buttons_container = QWidget()
        pixmap_buttons_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)    

        # Gestions des layouts
        spinbox_row.setContentsMargins(5, 5, 5, 5)
        spinbox_row.setSpacing(5)
        spinbox_row.addWidget(texte_type)
        spinbox_row.addWidget(self.bouton_type_image)
        spinbox_row.addWidget(self.bouton_type_video)
        spinbox_row.addWidget(self.bouton_type_documents)
        spinbox_row.addWidget(self.bouton_type_empty_folder)
        spinbox_container.setLayout(spinbox_row)
        
        layout_top_row.setContentsMargins(10, 10, 10, 10)
        layout_top_row.setSpacing(10)
        layout_top_row.addWidget(self.bouton_compte)
        layout_top_row.addWidget(spinbox_container)
        layout_top_row.addWidget(self.bouton_previsualisation)
        top_row_container.setLayout(layout_top_row)
        
        layout_right_buttons.setContentsMargins(10, 10, 10, 10)
        layout_right_buttons.setSpacing(10)
        layout_right_buttons.addWidget(self.bouton_pause)
        layout_right_buttons.addWidget(self.bouton_continuer)
        layout_right_buttons.addWidget(self.bouton_stop)
        layout_right_buttons.addWidget(self.bouton_retour_accueil)
        right_buttons_container.setLayout(layout_right_buttons)
        
        layout_pixmap_buttons.setContentsMargins(15, 15, 15, 15)
        layout_pixmap_buttons.setSpacing(15)
        layout_pixmap_buttons.addWidget(self.label_image, 0, 0)
        layout_pixmap_buttons.addWidget(right_buttons_container, 0, 1)
        pixmap_buttons_container.setLayout(layout_pixmap_buttons)
        
        layout_accueil.setContentsMargins(20, 20, 20, 20)
        layout_accueil.setSpacing(20)
        layout_accueil.addWidget(titre)
        layout_accueil.addWidget(top_row_container, 0, Qt.AlignCenter)
        layout_accueil.addWidget(pixmap_buttons_container, 0, Qt.AlignCenter)
        layout_accueil.addWidget(self.affichage, 0, Qt.AlignCenter)

        layout.addLayout(layout_accueil)
        self.setLayout(layout)

    def type_change(self, bouton):
        if bouton:
            logger.info("Changement de la liste de détection !")

            if bouton == self.bouton_type_image:
                if "Images" in self.type:
                    self.type.remove("Images")
                    bouton.setStyleSheet(style.cssBoutonErreur)

                else:
                    self.type.append("Images")
                    bouton.setStyleSheet(style.cssBoutonAcheve)

            elif bouton == self.bouton_type_video:
                if "Videos" in self.type:
                    self.type.remove("Videos")
                    bouton.setStyleSheet(style.cssBoutonErreur)

                else:
                    self.type.append("Videos")
                    bouton.setStyleSheet(style.cssBoutonAcheve)

            elif bouton == self.bouton_type_documents:
                if "Documents" in self.type:
                    self.type.remove("Documents")
                    bouton.setStyleSheet(style.cssBoutonErreur)

                else:
                    self.type.append("Documents")
                    bouton.setStyleSheet(style.cssBoutonAcheve)

            elif bouton == self.bouton_type_empty_folder:
                if "Empty Folder" in self.type:
                    self.type.remove("Empty Folder")
                    bouton.setStyleSheet(style.cssBoutonErreur)

                else:
                    self.type.append("Empty Folder")
                    bouton.setStyleSheet(style.cssBoutonAcheve)

        if len(self.type) == 1:
            if "Images" in self.type:
                self.bouton_type_image.setEnabled(False)

            elif "Videos" in self.type:
                self.bouton_type_video.setEnabled(False)

            elif "Documents" in self.type:
                self.bouton_type_documents.setEnabled(False)

            elif "Empty Folder" in self.type:
                self.bouton_type_empty_folder.setEnabled(False)

        elif len(self.type) > 1:
                self.bouton_type_image.setEnabled(True)
                self.bouton_type_video.setEnabled(True)
                self.bouton_type_documents.setEnabled(True)
                self.bouton_type_empty_folder.setEnabled(True)
        
        logger.debug(f"Voici les nouveaux types détectés : {self.type}")

    def cleanup_threads(self):
        """
        Nettoie tous les threads et workers existants.
        
        Cette méthode est appelée avant de créer de nouveaux threads
        pour éviter les conflits et les fuites mémoire.
        """
        logger.debug("Nettoyage des threads existants")
        
        # Nettoyage du worker
        if hasattr(self, 'worker') and self.worker is not None:
            try:
                self.worker.stop()
                self.worker.deleteLater()
            except:
                pass
            self.worker = None
        
        # Nettoyage du thread
        if hasattr(self, 'thread') and self.thread is not None:
            try:
                if self.thread.isRunning():
                    self.thread.quit()
                    self.thread.wait(1000)  # Attendre 1 seconde max
                    if self.thread.isRunning():
                        self.thread.terminate()
                        self.thread.wait(500)  # Attendre 500ms après terminate
                self.thread.deleteLater()
            except:
                pass
            self.thread = None
        
        logger.debug("Nettoyage des threads terminé")

    def parcours_photos(self):
        """
        Lance le parcours et catalogage des photos/vidéos OneDrive.
        
        Cette méthode:
        1. Configure l'interface pour le mode "en cours de traitement"
        2. Vide la base de données existante
        3. Lance un thread ParcoursPhotos pour explorer OneDrive
        4. Configure les connexions de signaux pour le retour d'information
        """
        
        # Nettoyage préventif des threads existants
        self.cleanup_threads()
        
        logger.info("Démarrage d'un nouveau parcours photos")
        
        # Activation des contrôles de gestion du processus
        self.bouton_stop.set_button(True) 
        self.bouton_pause.set_button(True)
        
        # Désactivation des contrôles non pertinents pendant le traitement
        self.bouton_compte.set_button(False)           
        self.bouton_previsualisation.set_button(False) 
        self.parent_interface.bouton_reconnect.set_button(False)        
        self.bouton_type_image.setEnabled(False)
        self.bouton_type_video.setEnabled(False)
        self.bouton_type_documents.setEnabled(False)
        self.bouton_type_empty_folder.setEnabled(False)

        # Remise à zéro de l'affichage
        self.label_image.pixmap_default()         
        self.affichage.change_text("Démarrage...")
        
        # Récupération de l'état de prévisualisation
        prev = self.bouton_previsualisation.isChecked()

        if prev:
            logger.info("La prévisualisation des médias est activé")
        else:
            logger.info("La prévisualisation des médias est désactivé")

        # Nettoyage de la base de données pour un nouveau parcours
        delete_sql()
        
        # Configuration du thread de parcours
        self.thread = QThread()
        self.worker = ParcoursPhotos(self.token, self.type, prev)
        self.worker.moveToThread(self.thread)

        # Configuration des connexions de signaux
        self.worker.image_ready.connect(self.afficher_preview)    # Prévisualisations
        self.worker.progression.connect(self.affichage.setText)   # Messages d'état
        self.worker.finished.connect(self.thread.quit)           # Nettoyage thread
        self.worker.finished.connect(self.worker.deleteLater)    # Nettoyage worker
        self.thread.finished.connect(self.thread.deleteLater)    # Nettoyage thread
        self.worker.finished.connect(self.thread_finished)       # Restauration interface
        
        # Démarrage du thread
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def thread_finished(self):
        """
        Restaure l'état de l'interface à la fin du parcours OneDrive.
        
        Cette méthode est appelée automatiquement quand le thread ParcoursPhotos
        se termine (succès, arrêt ou erreur).
        """
        # Désactivation des contrôles de gestion du processus
        self.bouton_pause.set_button(False)    
        self.bouton_continuer.set_button(False)
        self.bouton_stop.set_button(False)     
        
        # Réactivation des contrôles principaux
        self.bouton_previsualisation.set_button(True)
        self.bouton_compte.set_button(True)          
        self.parent_interface.bouton_reconnect.set_button(True)       
        self.bouton_type_image.setEnabled(True)
        self.bouton_type_video.setEnabled(True)
        self.bouton_type_documents.setEnabled(True)
        self.bouton_type_empty_folder.setEnabled(True)

    def afficher_preview(self, image_data:bytes):
        """
        Affiche une prévisualisation d'image en temps réel pendant le parcours.
        
        Cette méthode est appelée via signal depuis le worker ParcoursPhotos
        à chaque fois qu'une nouvelle image est traitée (si la prévisualisation
        est activée). Elle permet à l'utilisateur de voir le progrès visuel
        du parcours OneDrive.
        
        Args:
            image_data (bytes): Données binaires de l'image à afficher
            
        Gestion d'erreurs:
            Si l'image ne peut pas être chargée, l'erreur est loggée
            mais n'interrompt pas le processus de parcours.
        """
        try:
            # Conversion des données binaires en QPixmap pour l'affichage
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            
            # Affichage dans le widget d'image de l'interface
            self.label_image.set_image(pixmap)
            
            # Mise à jour immédiate de l'affichage (évite les délais)
            QApplication.processEvents()

        except Exception as e:
            # Log de l'erreur sans interrompre le processus principal
            logger.error(f"Problème avec la preview : {e}\n{traceback.format_exc()}")

    def pause(self):
        """
        Met en pause le parcours OneDrive en cours.
        
        Cette méthode:
        1. Signale au worker ParcoursPhotos de se mettre en pause
        2. Ajuste l'état des boutons pour refléter la pause
        3. Réactive certains contrôles (prévisualisation, reconnexion)
        """
        # Signal de pause au worker
        self.worker.pause_clear()
        
        # Désactivation du bouton pause (déjà en pause)
        self.bouton_pause.set_button(False)
        
        # Activation du bouton continuer
        self.bouton_continuer.set_button(True)
        
        # Réactivation des contrôles de configuration
        self.bouton_previsualisation.set_button(True)
        self.parent_interface.bouton_reconnect.set_button(True)     
        self.bouton_type_image.setEnabled(True)
        self.bouton_type_video.setEnabled(True)
        self.bouton_type_documents.setEnabled(True)    
        self.bouton_type_empty_folder.setEnabled(True)

    def continuer(self):
        """
        Reprend le parcours OneDrive après une pause.
        
        Cette méthode:
        1. Récupère l'état actuel de la prévisualisation
        2. Met à jour le worker avec les nouvelles préférences
        3. Signale au worker de reprendre le traitement
        4. Ajuste l'état des boutons pour refléter la reprise
        """
        
        # Vérification de l'état de prévisualisation (peut avoir changé pendant la pause)
        prev = self.bouton_previsualisation.isChecked()
        logger.debug(f"État de la prévisualisation à la reprise: {prev}")
        
        # Mise à jour du worker avec les nouvelles préférences
        self.worker.is_prev(prev)

        # Si prévisualisation désactivée, effacer l'image affichée
        if not prev:
            self.label_image.pixmap_default()
        
        # Signal de reprise au worker
        self.worker.pause_set()
        
        # Réactivation des contrôles de gestion du processus
        self.bouton_pause.set_button(True)
        
        # Désactivation des contrôles incompatibles avec traitement en cours
        self.bouton_continuer.set_button(False)       
        self.bouton_previsualisation.set_button(False) 
        self.parent_interface.bouton_reconnect.set_button(False)        
        self.bouton_type_image.setEnabled(False)
        self.bouton_type_video.setEnabled(False)
        self.bouton_type_documents.setEnabled(False)
        self.bouton_type_empty_folder.setEnabled(False)

    def stop(self):
        """
        Arrête complètement le parcours OneDrive en cours.
        
        Cette méthode:
        1. Signale au worker ParcoursPhotos d'arrêter le traitement
        2. Restaure l'interface dans un état "prêt pour nouveau parcours"
        3. Réactive tous les contrôles de configuration
        """
        logger.info("Arrêt du parcours demandé par l'utilisateur")
        
        try:
            # Signal d'arrêt au worker
            if hasattr(self, 'worker') and self.worker is not None:
                logger.debug("Envoi du signal d'arrêt au worker")
                self.worker.stop()
            
            # Arrêter le thread si il existe
            if hasattr(self, 'thread') and self.thread is not None:
                logger.debug("Arrêt du thread en cours")
                
                # Déconnecter tous les signaux pour éviter les appels après destruction
                try:
                    self.thread.started.disconnect()
                    if hasattr(self, 'worker') and self.worker is not None:
                        self.worker.image_ready.disconnect()
                        self.worker.progression.disconnect() 
                        self.worker.finished.disconnect()
                except:
                    pass  # Ignorer les erreurs de déconnexion
                
                self.thread.quit()
                
                # Attendre maximum 3 secondes pour que le thread se termine
                if not self.thread.wait(3000):  # 3000ms = 3 secondes
                    logger.warning("Le thread n'a pas pu être arrêté proprement, forçage...")
                    self.thread.terminate()
                    if not self.thread.wait(2000):  # 2 secondes supplémentaires après terminate
                        logger.error("Le thread refuse de se terminer, abandon du nettoyage")
                
                # Nettoyage des références
                self.thread.deleteLater()
                self.thread = None
                
            # Nettoyage du worker
            if hasattr(self, 'worker') and self.worker is not None:
                self.worker.deleteLater()
                self.worker = None
            
            # Force la finalisation de l'interface
            self.thread_finished()
            
            logger.info("Arrêt du thread terminé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt: {e}")
            # Force la restauration de l'interface en cas d'erreur
            self.thread_finished()
            # Nettoyage forcé en cas d'erreur
            self.thread = None
            self.worker = None       
        
        # Désactivation des contrôles de gestion du processus
        self.bouton_stop.set_button(False)     
        self.bouton_continuer.set_button(False)
        self.bouton_pause.set_button(False)    
        
        # Réactivation des contrôles principaux
        self.bouton_compte.set_button(True)          
        self.bouton_previsualisation.set_button(True)
        self.parent_interface.bouton_reconnect.set_button(True)

    def prev_turn(self):
        """
        Bascule l'état de la prévisualisation des images pendant le parcours.
        
        Cette méthode gère l'état du bouton de prévisualisation en mode toggle.
        Elle met à jour à la fois l'état visuel du bouton et son texte descriptif
        pour indiquer clairement à l'utilisateur si les prévisualisations
        seront affichées pendant le parcours OneDrive.
        
        États possibles:
        - Activé: "Prévisualisation activé" - Les images seront affichées
        - Désactivé: "Prévisualisation désactivé" - Parcours sans affichage
        """
        logger.info("Changement d'état de la prévisualisation")

        if not self.bouton_previsualisation.isChecked():
            self.bouton_previsualisation.setChecked(False)
            self.bouton_previsualisation.setText("Prévisualisation désactivé")

        else:
            self.bouton_previsualisation.setChecked(True)
            self.bouton_previsualisation.setText("Prévisualisation activé")

    def retour_accueil(self):
        """Retourne à la page d'accueil de l'application."""
        logger.info("Retour à l'accueil depuis la page des doublons")
        if self.parent_interface:
            self.parent_interface.stack.setCurrentIndex(0)