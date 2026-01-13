# token_security.py
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform
import uuid
from .logger import connecteLogger

logger = connecteLogger(__name__)

def get_machine_key():
    """
    Génère une clé unique basée sur cette machine
    Le token ne pourra être déchiffré que sur cette machine
    """
    machine_name = platform.node()
    mac_address = hex(uuid.getnode())
    system_info = platform.platform()
    
    machine_string = f"{machine_name}_{mac_address}_{system_info}"
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"duplicate_finder_2025",
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(machine_string.encode()))
    return key

def encrypt_token_file(token_data):
    """
    Chiffre les données du token et les sauvegarde
    
    Args:
        token_data: dictionnaire contenant le token
    
    Returns:
        True si succès, False sinon
    """
    try:
        key = get_machine_key()
        fernet = Fernet(key)
        
        token_json = json.dumps(token_data, indent=2)
        encrypted_data = fernet.encrypt(token_json.encode())
        
        with open("token.json.enc", "wb") as f:
            f.write(encrypted_data)
        
        logger.info("Token chiffré et sauvegardé dans token.json.enc")
        
        if os.path.exists("token.json"):
            os.remove("token.json")
            logger.info("Ancien token.json supprimé")
            
        return True
        
    except Exception as e:
        logger.info(f"Erreur lors du chiffrement: {e}")
        return False

def decrypt_token_file():
    """
    Déchiffre et charge les données du token
    
    Returns:
        Dictionnaire du token si succès, None sinon
    """
    try:
        if not os.path.exists("token.json.enc"):
            logger.warning("Aucun token chiffré trouvé")
            return None
        
        key = get_machine_key()
        fernet = Fernet(key)
        
        with open("token.json.enc", "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        token_data = json.loads(decrypted_data.decode())
        
        logger.info("Token déchiffré avec succès")
        return token_data
        
    except Exception as e:
        logger.warning(f"Erreur lors du déchiffrement: {e}")
        return None

def migrate_existing_token():
    """
    Migre un token.json existant vers la version chiffrée
    
    Returns:
        True si migration réussie ou pas nécessaire, False sinon
    """
    if os.path.exists("token.json.enc"):
        logger.debug("Token déjà chiffré")
        return True
    
    if not os.path.exists("token.json"):
        logger.info("ℹAucun token à migrer")
        return True
    
    try:
        with open("token.json", "r") as f:
            token_data = json.load(f)
        
        if encrypt_token_file(token_data):
            logger.info("Migration réussie: token.json → token.json.enc")
            return True
        else:
            logger.warning("Échec de la migration")
            return False
            
    except Exception as e:
        logger.warning(f"Erreur lors de la migration: {e}")
        return False

def delete_token_files():
    """
    Supprime tous les fichiers de token (chiffré et non chiffré)
    """
    deleted = False
    
    if os.path.exists("token.json.enc"):
        os.remove("token.json.enc")
        logger.debug("token.json.enc supprimé")
        deleted = True
    
    if os.path.exists("token.json"):
        os.remove("token.json")
        logger.info("token.json supprimé")
        deleted = True
    
    if not deleted:
        logger.info("Aucun token à supprimer")

def save_secure_token(token_data):
    return encrypt_token_file(token_data)

def load_secure_token():
    return decrypt_token_file()

def delete_secure_token():
    delete_token_files()
