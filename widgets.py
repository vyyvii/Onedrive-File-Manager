from PyQt5.QtWidgets import QLabel, QTextEdit, QPushButton, QScrollArea, QInputDialog
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QPixmap, QIcon
import os

import style #type: ignore
from fonctions.logger import connecteLogger

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

class Bouton(QPushButton):
    """
        Classe pour générer un bouton
    """

    def __init__(self, texte:str = "Bouton", connexion = None, activate:bool = True, height:int = 250, width:int = 70, check:bool = False, style = style.cssBouton):
        """
        Méthode constructeur
        """
        super().__init__()

        self.style_ = style

        self.setText(texte)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(QSize(height, width))
        self.setStyleSheet(self.style_)

        if connexion:
            self.clicked.connect(connexion)

        if check:
            self.setCheckable(True)

        self.set_button(activate)

    def set_button(self, activate):
        if not activate:
            self.setEnabled(False)
            self.setStyleSheet(style.cssBoutonDesactive)
            
            logger.info(f"{self} désactivé")

        else:
            self.setEnabled(True)
            self.setStyleSheet(self.style_)

            logger.info(f"{self} activé")

class LabelImage(QLabel):
    def __init__(self, width:int = 600, height:int = 400):
        """
        Widget personnalisé pour afficher des images
        """
        super().__init__()

        self.setStyleSheet(style.cssPixMap)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(width, height)
        self.pixmap_default()
    
    def pixmap_default(self):
        """Charge l'image par défaut OneDrive"""
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "content", "onedrive_logo.png"))
        self.setPixmap(pixmap.scaled(
            self.size().width() // 2,
            self.size().height() // 2, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
    
    def set_image(self, pixmap):
        """Définit une nouvelle image avec mise à l'échelle automatique"""
        if pixmap and not pixmap.isNull():
            self.setPixmap(pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

class Text(QLabel):
    def __init__(self, text:str = "Mon texte", style = style.cssSousTitre):
        super().__init__()

        self.setText(text)
        self.setStyleSheet(style)

class TextEdit(QTextEdit):
    def __init__(self, default_text:str = "Mon texte", heigt:int = 800, width:int = 200):
        super().__init__()

        self.setStyleSheet(style.cssZoneTexte)
        self.setReadOnly(True)
        self.setFixedSize(heigt, width)
        self.setText(default_text)

    def change_text(self, text:str):
        self.setText(text)

class ScrollArea(QScrollArea):
    def __init__(self, height, width, resize):
        super().__init__()
        
        self.setStyleSheet(style.cssScrollArea)
        self.setFixedSize(height, width)

        if resize:
            self.setWidgetResizable(resize)

class Animation(QPropertyAnimation):
    def __init__(self, target, property, duration:int = 300, start:int = 0.0, end:int = 1.0):
        super().__init__(target, property)

        self.setDuration(duration)
        self.setStartValue(start)
        self.setEndValue(end)
        self.start()

class InputDialog:
    @staticmethod
    def getInt(parent, window_title: str, label_texte: str, default: int = None, mini: int = None, maxi: int = None):
        dialog = QInputDialog(parent)
        dialog.setWindowTitle(window_title)
        dialog.setLabelText(label_texte)

        if mini is not None:
            dialog.setIntMinimum(mini)

        if maxi is not None:
            dialog.setIntMaximum(maxi)

        if default is not None:
            dialog.setIntValue(default)

        dialog.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "content", "settings_logo.png")))  # Logo dans la barre de titre

        ok = dialog.exec_()
        if ok == QInputDialog.Accepted:
            return dialog.intValue(), True
        
        else:
            return None, False
    
    @staticmethod
    def getItem(parent, window_title: str, label_texte: str, items: list, default: int, edit: bool):
        dialog = QInputDialog(parent)
        dialog.setWindowTitle(window_title)
        dialog.setLabelText(label_texte)
        dialog.setComboBoxItems(items)
        dialog.setComboBoxEditable(edit)

        if 0 <= default < len(items):
            dialog.setTextValue(items[default])

        dialog.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "content", "settings_logo.png")))  # Logo dans la barre de titre

        ok = dialog.exec_()
        if ok == QInputDialog.Accepted:
            return dialog.textValue(), True
        
        else:
            return None, False