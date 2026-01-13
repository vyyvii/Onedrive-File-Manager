# OneDrive Duplicate Finder - Documentation Technique

## Vue d'ensemble

OneDrive Duplicate Finder est une application PyQt5 qui permet de détecter et gérer les doublons de photos et vidéos stockés sur Microsoft OneDrive. L'application utilise l'API Microsoft Graph pour accéder aux fichiers et propose deux méthodes de détection : par critères exacts et par similarité visuelle.

## Table des matières

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Utilisation](#utilisation)
5. [API et modules](#api-et-modules)
6. [Base de données](#base-de-données)
7. [Algorithmes de détection](#algorithmes-de-détection)
8. [Gestion des erreurs](#gestion-des-erreurs)
9. [Développement](#développement)

## Architecture

### Structure du projet

```
Projet de l'été/
├── main.py                 # Interface principale et logique applicative
├── style.py               # Styles et thèmes de l'interface
├── widgets.py             # Widgets personnalisés PyQt5
├── config.cfg             # Configuration de l'application
├── token.json             # Stockage sécurisé des tokens OAuth2
├── picture_video.db       # Base de données SQLite des métadonnées
├── fonctions/             # Modules fonctionnels
│   ├── config.py          # Gestion de la configuration
│   ├── graph.py           # Interface API Microsoft Graph
│   ├── logger.py          # Système de journalisation
│   ├── server.py          # Serveur OAuth2 local
│   ├── sql.py             # Opérations base de données
│   └── token_manager.py   # Gestion des tokens d'authentification
├── content/               # Ressources graphiques
│   ├── onedrive_logo.png
│   └── settings_logo.png
├── logs/                  # Fichiers de journalisation
└── save/                  # Sauvegardes automatiques
```

### Composants principaux

#### 1. Interface utilisateur (main.py)
- **Interface** : Classe principale gérant la fenêtre et l'authentification
- **Doublons** : Interface de gestion et visualisation des doublons
- Widgets personnalisés pour l'affichage des images et contrôles

#### 2. Threads de traitement
- **ParcoursPhotos** : Exploration récursive d'OneDrive
- **ThreadHashNomTaille** : Détection par critères exacts
- **ThreadVisuel** : Détection par similarité visuelle
- **ThreadPreview** : Génération de prévisualisations

#### 3. Modules fonctionnels
- **graph.py** : Interactions avec l'API Microsoft Graph
- **sql.py** : Opérations sur la base de données SQLite
- **token_manager.py** : Authentification OAuth2
- **logger.py** : Journalisation centralisée

## Installation

### Prérequis
- Python 3.8+
- Compte Microsoft avec accès OneDrive
- Application Microsoft Graph enregistrée

### Dépendances
```bash
pip install PyQt5 requests imagehash pillow numpy sqlite3
```

### Configuration Microsoft Graph
1. Créer une application sur [Azure Portal](https://portal.azure.com)
2. Configurer les permissions Microsoft Graph :
   - `Files.Read.All`
   - `Files.ReadWrite.All`
   - `User.Read`
3. Ajouter l'URI de redirection : `http://localhost:8080/callback`

## Configuration

### Fichier config.cfg
```ini
[API]
client_id = votre-client-id
client_secret = votre-client-secret
redirect_uri = http://localhost:8080/callback
scopes = https://graph.microsoft.com/Files.Read.All https://graph.microsoft.com/Files.ReadWrite.All https://graph.microsoft.com/User.Read

[DATABASE]
db_name = picture_video.db
backup_enabled = true

[LOGGING]
level = INFO
max_files = 10
```

## Utilisation

### Démarrage
```bash
python main.py
```

### Flux de travail

1. **Authentification** : Connexion automatique via OAuth2
2. **Parcours** : Exploration des dossiers OneDrive
3. **Détection** : Recherche de doublons par méthode choisie
4. **Visualisation** : Comparaison visuelle des doublons
5. **Action** : Suppression sélective des fichiers

### Méthodes de détection

#### Critères exacts
- Noms de fichiers identiques
- Tailles identiques
- Hash SHA256 identiques
- Hash perceptuels identiques

#### Similarité visuelle
- Comparaison de hash perceptuels (pHash)
- Seuil de similarité configurable (0-30)
- Détection d'images modifiées (compression, redimensionnement)

## API et modules

### graph.py - Interface Microsoft Graph

```python
def call_web_api(endpoint, token, select=None, method="get"):
    """
    Effectue un appel à l'API Microsoft Graph
    
    Args:
        endpoint (str): Point d'accès API
        token (str): Token d'authentification
        select (list): Champs à récupérer
        method (str): Méthode HTTP
    
    Returns:
        dict|int: Données JSON ou code de statut
    """
```

### sql.py - Base de données

```python
def insert_sql(object, curseur, connexion, phash=None):
    """
    Insère un fichier en base de données
    
    Args:
        object (dict): Métadonnées du fichier OneDrive
        curseur: Curseur SQLite
        connexion: Connexion SQLite
        phash (str): Hash perceptuel optionnel
    """
```

### token_manager.py - Authentification

```python
def get_access_token():
    """
    Récupère un token valide depuis le stockage
    
    Returns:
        str|None: Token d'accès ou None si expiré
    """
```

## Base de données

### Schéma SQLite

```sql
CREATE TABLE picture_video (
    id TEXT PRIMARY KEY,           -- ID OneDrive unique
    type TEXT,                     -- Type MIME
    name TEXT,                     -- Nom du fichier
    size INTEGER,                  -- Taille en octets
    hash TEXT,                     -- Hash SHA256
    createdDateTime TEXT,          -- Date de création
    lastModifiedDateTime TEXT,     -- Date de modification
    phash TEXT,                    -- Hash perceptuel (images uniquement)
    path TEXT                      -- Chemin du dossier parent
);
```

### Index de performance
- Index primaire sur `id`
- Index composé sur `name, size`
- Index sur `hash`
- Index sur `phash`

## Algorithmes de détection

### Hash perceptuel (pHash)
```python
# Génération du hash perceptuel 16x16
hash_result = str(imagehash.phash(img, hash_size=16))

# Calcul de la distance de Hamming
distance = hash1 - hash2

# Détection de similarité selon seuil
if distance <= seuil:
    # Images similaires détectées
```

### Métriques de similarité
1. **Similarité de base** : `(hash_size - distance) / hash_size * 100`
2. **Similarité fine** : Comparaison bit par bit
3. **Similarité par clusters** : Analyse par groupes de 4 bits
4. **Similarité globale** : Moyenne pondérée (50% base + 30% fine + 20% clusters)

## Gestion des erreurs

### Stratégies implémentées
- **Try/catch** sur les appels réseau
- **Retry automatique** pour les timeouts API
- **Logs détaillés** de toutes les erreurs
- **Interface non-bloquante** en cas d'erreur

### Codes d'erreur courants
- **401** : Token expiré → Reconnexion automatique
- **404** : Fichier supprimé → Ignore et continue
- **429** : Rate limiting → Attente et retry
- **500** : Erreur serveur → Retry avec backoff

## Développement

### Structure des classes

```python
class ParcoursPhotos(QObject):
    """Worker thread pour l'exploration OneDrive"""
    
    def run(self):
        """Point d'entrée principal du parcours"""
    
    def folder_list(self, data):
        """Traite les éléments d'un dossier"""
    
    def preview(self, id, type):
        """Génère preview et hash perceptuel"""
```

### Signaux PyQt5
- `progression(str)` : Messages de progression
- `image_ready(bytes)` : Données d'image pour preview
- `finished()` : Fin de traitement

### Threading
- **QThread** pour les opérations longues
- **Signaux/slots** pour la communication inter-threads
- **Events** pour le contrôle pause/stop

### Bonnes pratiques
1. **Gestion mémoire** : Suppression explicite des threads
2. **Interface non-bloquante** : Toutes les opérations longues en thread
3. **Logs structurés** : Niveaux DEBUG, INFO, WARNING, ERROR
4. **Gestion d'état** : Sauvegarde/restauration de l'état interface

## Tests et débogage

### Logs
```bash
# Fichiers dans /logs/
log_YYYY-MM-DD_HH-MM-SS.log
```

### Niveaux de log
- **DEBUG** : Détails techniques
- **INFO** : Opérations normales
- **WARNING** : Situations non critiques
- **ERROR** : Erreurs nécessitant attention

### Base de données de test
```python
# Sauvegarde automatique avant parcours
cp picture_video.db save/picture_video_save.db
```

## Performances

### Optimisations
- **Pagination API** : 200 éléments par requête
- **Cache local** : Métadonnées en SQLite
- **Hash parallèle** : Calcul pendant téléchargement
- **Preview adaptative** : Désactivable pour vitesse

### Métriques
- **Parcours** : ~1000 fichiers/minute (avec preview)
- **Détection exacte** : ~10000 comparaisons/seconde
- **Détection visuelle** : ~100 comparaisons/seconde
- **Mémoire** : <200MB pour 50000 fichiers

## Sécurité

### Authentification
- **OAuth2** avec refresh token
- **Stockage sécurisé** des tokens (chiffrement local)
- **Expiration automatique** des sessions

### API
- **Rate limiting** respecté
- **HTTPS uniquement**
- **Permissions minimales** requises

### Données
- **Base locale** uniquement
- **Pas de transfert** de fichiers
- **Métadonnées anonymisées** dans les logs

## Support et maintenance

### Résolution de problèmes
1. Vérifier les logs dans `/logs/`
2. Tester la connectivité OneDrive
3. Régénérer les tokens d'authentification
4. Vérifier les permissions Microsoft Graph

### Mises à jour
- **Backward compatibility** assurée
- **Migration automatique** de la base de données
- **Configuration préservée** entre versions

### Contact
- **Documentation** : Ce fichier
- **Issues** : Logs détaillés requis
- **Fonctionnalités** : Requests avec cas d'usage

---

*Dernière mise à jour : Juillet 2025*
*Version : 1.0*
