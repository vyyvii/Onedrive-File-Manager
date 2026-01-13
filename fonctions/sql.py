import sqlite3
from .logger import connecteLogger

# ==============
# === LOGGER ===
# ==============
logger = connecteLogger(__name__)

connexion_loc = sqlite3.connect("picture_video.db")
curseur_loc = connexion_loc.cursor()

def insert_sql(object, curseur, connexion, phash:str):
    id = object.get('id')
    type = object.get('file').get('mimeType')
    name = object.get('name')
    size = object.get('size')
    hash = object.get('file').get('hashes').get('sha256Hash')
    createdDateTime = object.get('createdDateTime')
    lastModifiedDateTime = object.get('lastModifiedDateTime')
    path = object.get('parentReference').get('path')

    logger.debug(f"Insertion SQL dans picture_video: {name} (ID: {id})")
    curseur.execute("""
        INSERT INTO picture_video (
            id, type, name, size, hash, createdDateTime, lastModifiedDateTime, phash, path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id, type, name, size, hash, createdDateTime, lastModifiedDateTime, phash, path))

    connexion.commit()

def insert_sql_empty_folder(object, curseur, connexion):
    id = object.get('id')
    name = object.get('name')
    size = object.get('size')
    path = object.get('parentReference').get('path')

    logger.debug(f"Insertion SQL dans empty_folder: {name} (ID: {id})")
    curseur.execute("""
        INSERT INTO empty_folder (
            id, name, size, path
        ) VALUES (?, ?, ?, ?)
    """, (id, name, size, path))

    connexion.commit()

def compte_db(curseur = curseur_loc, db = "picture_video"):
    curseur.execute(f"""
        SELECT COUNT(id) FROM {db}
    """)
    resultat = curseur.fetchone()
    nombre_lignes = resultat[0]
    logger.info(f"Total d'entrées en base: {nombre_lignes}")

    return nombre_lignes

def delete_sql(curseur = curseur_loc, connexion = connexion_loc):
    logger.info("Suppression de toutes les données de la base")
    curseur.execute("""
        DELETE FROM picture_video;
    """)
    curseur.execute("""
        DELETE FROM empty_folder;
    """)

    connexion.commit()
    logger.debug("Base de données vidée avec succès")

def tri_doublons(sort_by:str, out:str = None, curseur = curseur_loc):
    if not out:
        out = sort_by

    curseur.execute(f"""
        SELECT name, type, {out}, id, path 
        FROM picture_video
        WHERE {sort_by} IN (
            SELECT {sort_by}
            FROM picture_video
            GROUP BY {sort_by}
            HAVING COUNT(*) = 2
        )
        ORDER BY {sort_by}
    """)
    resultat = curseur.fetchall()
    logger.info(f"Trouvé {len(resultat)} doublons basés sur {sort_by}")

    return resultat

def recup_useless(curseur = curseur_loc):
    curseur.execute(f"""
        SELECT name, type, size, id, path, lastModifiedDateTime
        FROM picture_video
    """)
    resultat = curseur.fetchall()
    logger.info(f"Recup_useless a renvoyé {len(resultat)} lignes")

    return resultat

def recup_phash(curseur = curseur_loc):
    logger.debug("Récupération des hashes perceptuels")
    curseur.execute("""
        SELECT name, type, size, id, phash, path 
        FROM picture_video 
        WHERE phash IS NOT NULL AND phash != ''   
    """)
    resultat = curseur.fetchall()
    logger.info(f"Récupéré {len(resultat)} fichiers avec hash perceptuel, {resultat}")

    return resultat

def recup_folder(curseur = curseur_loc):
    logger.debug("Récupération des hashes perceptuels")
    curseur.execute("""
        SELECT id, name, size, path
        FROM empty_folder
    """)

    resultat = curseur.fetchall()
    logger.info(f"Récupéré {len(resultat)} dossiers vides")

    return resultat

logger.info("Initialisation de la base de données")
curseur_loc.execute("""
    CREATE TABLE IF NOT EXISTS picture_video (
        id TEXT PRIMARY KEY,
        type TEXT,
        name TEXT,
        size INTEGER,
        hash TEXT,
        createdDateTime TEXT,
        lastModifiedDateTime TEXT,
        phash TEXT,
        path TEXT
    )
""")
curseur_loc.execute("""
    CREATE TABLE IF NOT EXISTS empty_folder (
        id TEXT PRIMARY KEY,
        name TEXT,
        size INTEGER,
        path TEXT
    )
""")
connexion_loc.commit()
logger.debug("Table picture_video créée ou vérifiée")