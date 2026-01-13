# OneDrive Duplicate Finder

🔍 **Détectez et gérez efficacement les doublons de photos et vidéos dans votre OneDrive**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)

## 🎯 Fonctionnalités principales

- ✅ **Détection intelligente** : Deux méthodes de détection (critères exacts + similarité visuelle)
- 🔐 **Sécurisé** : Authentification OAuth2 avec Microsoft Graph API
- 🖼️ **Prévisualisation** : Comparaison visuelle côte à côte des doublons
- ⚡ **Performant** : Traitement en arrière-plan avec interface non-bloquante
- 🗂️ **Gestion avancée** : Suppression sélective directement depuis OneDrive
- 📊 **Statistiques** : Rapports détaillés du parcours et des doublons trouvés

## 📸 Captures d'écran

### Interface principale
![Interface principale](./docs/screenshots/main_interface.png)

### Détection de doublons
![Détection de doublons](./docs/screenshots/duplicate_detection.png)

### Comparaison visuelle
![Comparaison visuelle](./docs/screenshots/visual_comparison.png)

## 🚀 Installation rapide

### Prérequis
- Python 3.8 ou supérieur
- Compte Microsoft avec OneDrive
- Application Microsoft Graph (voir [Configuration](#⚙️-configuration))

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/onedrive-duplicate-finder.git
cd onedrive-duplicate-finder
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'authentification
```bash
cp config.cfg.example config.cfg
# Éditer config.cfg avec vos identifiants Microsoft Graph
```

### 4. Lancer l'application
```bash
python main.py
```

## ⚙️ Configuration

### Création d'une application Microsoft Graph

1. **Accéder au portail Azure**
   - Aller sur [portal.azure.com](https://portal.azure.com)
   - Se connecter avec votre compte Microsoft

2. **Enregistrer une nouvelle application**
   ```
   Azure Active Directory > Inscriptions d'applications > Nouvelle inscription
   
   Nom : OneDrive Duplicate Finder
   Types de comptes pris en charge : Comptes personnels Microsoft uniquement
   URI de redirection : http://localhost:8080/callback
   ```

3. **Configurer les permissions**
   ```
   API autorisées > Ajouter une autorisation > Microsoft Graph > Autorisations déléguées
   
   ✅ Files.Read.All
   ✅ Files.ReadWrite.All  
   ✅ User.Read
   ```

4. **Récupérer les identifiants**
   ```
   Vue d'ensemble > ID d'application (client) > Copier
   Certificats et secrets > Nouveau secret client > Copier la valeur
   ```

### Fichier de configuration

Créer `config.cfg` :
```ini
[API]
client_id = votre-client-id-ici
client_secret = votre-client-secret-ici
redirect_uri = http://localhost:8080/callback
scopes = https://graph.microsoft.com/Files.Read.All https://graph.microsoft.com/Files.ReadWrite.All https://graph.microsoft.com/User.Read

[DATABASE]
db_name = picture_video.db
backup_enabled = true

[LOGGING]
level = INFO
max_files = 10
```

## 📖 Guide d'utilisation

### 1. Premier lancement
- L'application s'ouvre et demande l'authentification Microsoft
- Une page web s'ouvre pour saisir vos identifiants
- Une fois connecté, vous revenez à l'interface principale

### 2. Parcours des fichiers
- **Configurer** : Ajuster le nombre max d'éléments par dossier (défaut: 5000)
- **Prévisualisation** : Activer pour voir les images pendant le parcours (plus lent)
- **Lancer** : Cliquer sur "Compter mes photos" pour démarrer l'exploration
- **Contrôler** : Utiliser Pause/Continuer/Stop selon vos besoins

### 3. Détection de doublons

#### Méthode "Nom, taille et hash"
- ✅ **Rapide** : Détection en quelques secondes
- ✅ **Précise** : Doublons exactement identiques
- ❌ **Limitée** : Ne détecte pas les copies modifiées

#### Méthode "Visuel"
- ✅ **Intelligente** : Détecte les images similaires même redimensionnées
- ✅ **Configurable** : Seuil de similarité ajustable (0-30)
- ❌ **Plus lente** : Requiert les hash perceptuels

### 4. Gestion des doublons
- **Naviguer** : Utiliser les boutons Précédent/Suivant
- **Comparer** : Voir les images côte à côte avec chemins complets
- **Supprimer** : Cliquer sur "Supprimer" sous l'image à éliminer
- **Statistiques** : Consulter le nombre total de doublons trouvés

## 🔧 Architecture technique

### Structure du projet
```
📁 onedrive-duplicate-finder/
├── 📄 main.py                 # Interface principale et logique applicative
├── 📄 style.py               # Styles et thèmes PyQt5
├── 📄 widgets.py             # Widgets personnalisés
├── 📄 config.cfg             # Configuration utilisateur
├── 📄 requirements.txt       # Dépendances Python
├── 📁 fonctions/             # Modules fonctionnels
│   ├── 📄 graph.py           # API Microsoft Graph
│   ├── 📄 logger.py          # Système de logs
│   ├── 📄 server.py          # Serveur OAuth2
│   ├── 📄 sql.py             # Base de données SQLite
│   └── 📄 token_manager.py   # Gestion authentification
├── 📁 content/               # Ressources graphiques
├── 📁 logs/                  # Fichiers de journalisation
└── 📁 save/                  # Sauvegardes automatiques
```

### Technologies utilisées
- **Interface** : PyQt5 pour l'interface graphique native
- **API** : Microsoft Graph pour l'accès OneDrive
- **Base de données** : SQLite pour le stockage local des métadonnées
- **Images** : PIL + imagehash pour la détection visuelle
- **Threading** : QThread pour les opérations non-bloquantes
- **Authentification** : OAuth2 avec refresh tokens

### Algorithmes de détection

#### Hash perceptuel (pHash)
```python
# Génération d'un hash 16x16 pour chaque image
hash_result = str(imagehash.phash(img, hash_size=16))

# Calcul de la distance de Hamming entre deux hash
distance = hash1 - hash2

# Détection selon le seuil configuré
is_similar = distance <= seuil_utilisateur
```

#### Métriques de similarité avancées
1. **Similarité de base** : Distance de Hamming normalisée
2. **Similarité fine** : Comparaison bit par bit
3. **Similarité par clusters** : Analyse par groupes de pixels
4. **Score global** : Moyenne pondérée des trois métriques

## 📊 Performances

### Métriques typiques
- **Parcours** : 500-1500 fichiers/minute (selon taille OneDrive)
- **Détection exacte** : 10000+ comparaisons/seconde
- **Détection visuelle** : 50-200 comparaisons/seconde
- **Mémoire** : <200MB pour 50000 fichiers catalogués

### Optimisations
- ✅ Pagination intelligente des requêtes API
- ✅ Cache local des métadonnées
- ✅ Calcul parallèle des hash perceptuels
- ✅ Interface responsive pendant les traitements

## 🐛 Résolution de problèmes

### Problèmes courants

#### "Erreur d'authentification"
```bash
# Solution 1 : Vérifier la configuration
cat config.cfg

# Solution 2 : Supprimer les tokens et se reconnecter
rm token.json
python main.py
```

#### "Aucune image trouvée"
- ✅ Vérifier que OneDrive contient des photos/vidéos
- ✅ Augmenter la limite d'éléments par dossier
- ✅ Consulter les logs dans `/logs/`

#### "Détection visuelle lente"
- ✅ Réduire le seuil de similarité
- ✅ Filtrer d'abord par critères exacts
- ✅ Désactiver la prévisualisation pendant le parcours

### Logs et diagnostic
```bash
# Consulter les logs les plus récents
ls -la logs/
tail -f logs/log_2025-*.log

# Niveau de détail
# DEBUG : Informations techniques détaillées
# INFO  : Opérations normales
# WARN  : Situations non critiques
# ERROR : Erreurs nécessitant attention
```

## 🤝 Contribution

### Comment contribuer
1. **Fork** ce repository
2. **Créer** une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. **Commiter** vos changements (`git commit -m 'Add amazing feature'`)
4. **Pusher** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### Standards de code
- **PEP 8** pour le style Python
- **Docstrings** détaillées pour toutes les fonctions
- **Tests unitaires** pour les nouvelles fonctionnalités
- **Logs** appropriés pour le débogage

### Roadmap
- [ ] Support des autres clouds (Google Drive, Dropbox)
- [ ] Interface web responsive
- [ ] API REST pour intégrations
- [ ] Mode ligne de commande
- [ ] Détection de doublons audio/vidéo
- [ ] Analyse par intelligence artificielle

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

```
MIT License

Copyright (c) 2025 Victor Defauchy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 👨‍💻 Auteur

**Victor Defauchy**
- 🌐 Site web : [duplicatefinder.fr](https://duplicatefinder.fr)
- 📧 Email : contact@duplicatefinder.fr
- 💼 LinkedIn : [Victor Defauchy](https://linkedin.com/in/victor-defauchy)

## 🙏 Remerciements

- **Microsoft Graph API** pour l'accès OneDrive
- **PyQt5** pour le framework d'interface
- **ImageHash** pour les algorithmes de détection visuelle
- **Communauté Python** pour les outils et bibliothèques

---

⭐ **N'hésitez pas à donner une étoile si ce projet vous a été utile !**

---

*Dernière mise à jour : Juillet 2025 | Version 1.0*
