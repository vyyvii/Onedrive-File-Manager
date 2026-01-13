# server.py
from flask import Flask, request
from threading import Event

from .logger import connecteLogger

logger = connecteLogger(__name__)
app = Flask(__name__)

@app.route("/")
def receive_code():
    global auth_code
    code = request.args.get("code")

    if code:
        auth_code = code
        auth_code_event.set()

        logger.info("Authentification réussie")

        return """
        <html>
            <head>
                <meta charset="utf-8" />
                <title>Granted</title>
                <style>
                    body {
                    background-color: #1ea2e7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    }
                    .container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    }
                    h1 {
                    color: white;
                    font-size: 80px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 10px;
                    font-family: Arial;
                    }
                    h2 {
                    color: white;
                    font-size: 40px;
                    text-align: center;
                    margin-top: 0;
                    font-family: Arial;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>OneDrive Duplicate Finder</h1>
                    <h2>Authentification réussie ! Vous pouvez retourner dans l'application.</h2>
                </div>
            </body>
        </html>
        """
    
    logger.warning("ERREUR lors de l'authentification")

    return "Erreur lors de l'authentification"

def wait_for_code():
    logger.info("Code en attente")

    auth_code_event.wait()
    return auth_code

def start_server():
    logger.info("Serveur Flask démarré sur le port 8000")

    app.run(port=8000, debug=False)

auth_code_event = Event()
auth_code = None