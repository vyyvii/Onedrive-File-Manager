import configparser
import msal
import os

def config_loader(file):
    """
    Method use for extract values of config.cfg
    """
    config = configparser.ConfigParser()
    config.read(file)

    settings = config['azure']

    CLIENT_ID = settings['clientId']
    TENANT_ID = 'common'
    CLIENT_SECRET = settings['clientSecret']

    azure_settings = (CLIENT_ID, TENANT_ID, CLIENT_SECRET)

    return azure_settings

chemin_config = os.path.join(os.path.dirname(__file__), "..", "config.cfg")
chemin_token = os.path.join(os.path.dirname(__file__), "..", "token.json")

CLIENT_ID, TENANT_ID, CLIENT_SECRET = config_loader(chemin_config)
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ['Files.ReadWrite.All', 'User.Read']
REDIRECT_URI = "http://localhost:8000/"
TOKEN_FILE = chemin_token

app_msal = msal.ConfidentialClientApplication(
    client_id = CLIENT_ID,
    client_credential = CLIENT_SECRET,
    authority = AUTHORITY
)