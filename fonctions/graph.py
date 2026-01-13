# graph.py
import requests

from .logger import connecteLogger

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

def call_web_api(endpoint, token, select = None, request_type = "get"):
    """
    Method use for make a request to the endpoind in parameter
    """
    if not token:
        logger.error("Token manquant ou None - impossible de faire l'appel API")
        return None
        
    url = f'https://graph.microsoft.com/v1.0/{endpoint}'
    logger.debug(f"Appel API {request_type.upper()}: {endpoint}")

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {}

    if select:
        params['$select'] = ','.join(select) if isinstance(select, list) else select

    if request_type == "get":
        data = requests.get(url, headers = headers, params = params)
        
    elif request_type == "delete":
        data = requests.delete(url, headers = headers, params = params)

        if data.status_code == 404:
            logger.warning(f"ERREUR : {data.status_code} {data.text}")

            return data.status_code

    if data.status_code == 200:
        response = data.json()
        logger.debug(f"Réponse API 200 OK - Endpoint: {endpoint}")

        return response
    
    elif data.status_code == 204:
        logger.info(f"Requête DELETE réussie - Endpoint: {endpoint}")

        return data.status_code

    else:
        logger.error(f"ERREUR API {data.status_code}: {data.text} - Endpoint: {endpoint}")

        return None
