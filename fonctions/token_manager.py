# token_manager.py
import time

from .config import app_msal, SCOPES, REDIRECT_URI
from .logger import connecteLogger
from fonctions.token_security import save_secure_token, load_secure_token, delete_secure_token

logger = connecteLogger(__name__)

def save_token(token_data):
    logger.debug("Sauvegarde du token")
    return save_secure_token(token_data)

def load_token():
    logger.debug("Tentative de chargement du token")
    return load_secure_token()

def is_token_expired(token_data):
    if time.time() > token_data.get("expires_at", 0):
        logger.info("Token expiré")

        return True
    
    else:
        logger.info("Token non expiré")

        return False

def get_access_token():
    logger.debug("Récupération du token d'accès")
    token_data = load_token()

    if token_data and not is_token_expired(token_data):
        access_token = token_data["access_token"]

        logger.info(f"Le token est présent dans le fichier")

        return access_token

    if token_data and "refresh_token" in token_data:
        logger.info("Tentative de rafraîchissement du token")
        refreshed = app_msal.acquire_token_by_refresh_token(
            token_data["refresh_token"],
            scopes=SCOPES
        )

        if "access_token" in refreshed:
            logger.info("Token rafraîchi avec succès")
            refreshed["expires_at"] = time.time() + int(refreshed["expires_in"])
            save_token(refreshed)
            return refreshed["access_token"]
        else:
            logger.warning("Échec du rafraîchissement du token")

    return None

def build_auth_url():
    url = app_msal.get_authorization_request_url(
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI,
        prompt = "consent"
    )

    logger.info(f"URL généré : {url}")

    return url

def acquire_token_by_code(auth_code):
    result = app_msal.acquire_token_by_authorization_code(
        auth_code,
        scopes = SCOPES,
        redirect_uri = REDIRECT_URI
    )

    if "access_token" in result:
        result["expires_at"] = time.time() + int(result["expires_in"])
        save_token(result)

        logger.info(f"Token acquis, expire : {result["expires_at"]}")

        return result["access_token"]
    
    else:
        logger.warning("Erreur de récupération du token par code : " + str(result.get("error_description")))

def delete_token():
    delete_secure_token()
