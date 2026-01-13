# Déclaration de Confidentialité

**OneDrive Duplicate Finder**

*Dernière mise à jour : 31 juillet 2025*

## Introduction

Chez OneDrive Duplicate Finder, nous nous engageons à protéger votre vie privée et vos données personnelles. Cette Déclaration de Confidentialité explique comment nous collectons, utilisons, stockons et protégeons vos informations lorsque vous utilisez notre application.

## 1. Responsable du traitement

**Victor Defauchy**
- Email : contact@duplicatefinder.fr
- Site web : https://duplicatefinder.fr

En tant que développeur et distributeur de OneDrive Duplicate Finder, Victor Defauchy est le responsable du traitement de vos données personnelles au sens du RGPD.

## 2. Données collectées

### 2.1 Données collectées directement

#### Informations de profil Microsoft
Avec votre autorisation explicite, nous accédons à :
- **Nom d'affichage** : Pour personnaliser l'interface utilisateur
- **Adresse email** : Pour identifier votre compte (affichage uniquement)
- **ID utilisateur Microsoft** : Pour maintenir la session d'authentification

#### Métadonnées de fichiers OneDrive
L'application analyse uniquement les métadonnées de vos fichiers :
- **Noms de fichiers** : Pour identifier les doublons potentiels
- **Tailles de fichiers** : Pour la détection par critères exacts
- **Hash SHA256** : Fournis par OneDrive pour l'intégrité des fichiers
- **Dates de création et modification** : Pour l'affichage et le tri
- **Chemins des dossiers** : Pour localiser les fichiers dans votre OneDrive
- **Types MIME** : Pour identifier les photos et vidéos

#### Hash perceptuels (optionnel)
Si vous activez la détection visuelle :
- **Hash perceptuels (pHash)** : Calculés localement à partir des miniatures
- **Miniatures** : Téléchargées temporairement pour le calcul des hash et prévisualisation

### 2.2 Données techniques automatiques

#### Journalisation (logs)
L'application génère automatiquement des logs locaux contenant :
- **Horodatages** : Date et heure des opérations
- **Niveaux de log** : DEBUG, INFO, WARNING, ERROR
- **Messages techniques** : États des opérations, erreurs rencontrées
- **Statistiques d'utilisation** : Nombre de fichiers traités, durée des opérations

**Important** : Les logs ne contiennent jamais le contenu des fichiers, seulement des métadonnées anonymisées.

#### Données d'authentification
- **Tokens OAuth2** : Stockés localement de manière chiffrée
- **Refresh tokens** : Pour le renouvellement automatique des sessions
- **Timestamps d'expiration** : Pour la gestion automatique des sessions

### 2.3 Données NOT collectées

Nous NE collectons JAMAIS :
- ❌ Le contenu complet de vos photos ou vidéos
- ❌ Vos identifiants Microsoft (mot de passe)
- ❌ Votre historique de navigation
- ❌ Vos contacts ou autres données personnelles
- ❌ Votre localisation géographique
- ❌ Des données de tracking ou analytics

## 3. Base légale du traitement

### 3.1 Consentement (Art. 6.1.a RGPD)
- **Accès OneDrive** : Vous autorisez explicitement l'accès via OAuth2
- **Détection visuelle** : Vous activez volontairement cette fonctionnalité
- **Suppression de fichiers** : Chaque suppression nécessite une action volontaire

### 3.2 Intérêt légitime (Art. 6.1.f RGPD)
- **Logs techniques** : Nécessaires au fonctionnement et débogage de l'application
- **Optimisation des performances** : Cache local des métadonnées

### 3.3 Exécution d'un contrat (Art. 6.1.b RGPD)
- **Fourniture du service** : Traitement nécessaire pour fournir les fonctionnalités promises

## 4. Finalités du traitement

### 4.1 Finalités principales
- **Détection de doublons** : Identification des fichiers identiques ou similaires
- **Comparaison visuelle** : Affichage côte à côte pour aide à la décision
- **Gestion des fichiers** : Suppression sélective des doublons non désirés
- **Statistiques** : Rapports sur les fichiers analysés et doublons trouvés

### 4.2 Finalités techniques
- **Authentification** : Maintien de la session utilisateur sécurisée
- **Performance** : Cache local pour éviter les appels API répétés
- **Débogage** : Logs pour identifier et résoudre les problèmes techniques
- **Sécurité** : Vérification de l'intégrité des données

## 5. Stockage et localisation des données

### 5.1 Stockage local uniquement
**TOUTES vos données sont stockées exclusivement sur votre appareil local :**
- Base de données SQLite : `picture_video.db`
- Fichiers de logs : Dossier `/logs/`
- Tokens d'authentification : `token.json` (chiffré)
- Configuration : `config.cfg`

### 5.2 Aucun transfert vers nos serveurs
- ✅ Aucune donnée personnelle n'est transmise à nos serveurs
- ✅ Aucun tracking ou télémétrie
- ✅ Aucune sauvegarde automatique dans le cloud
- ✅ Fonctionnement 100% local après authentification

### 5.3 Interactions avec Microsoft
Les seules communications externes sont avec Microsoft Graph API :
- **Authentification OAuth2** : Selon les standards Microsoft
- **Requêtes API** : Pour accéder aux métadonnées de vos fichiers OneDrive
- **Chiffrement HTTPS** : Toutes les communications sont sécurisées

## 6. Durée de conservation

### 6.1 Données de session
- **Tokens d'accès** : 1 heure (renouvelés automatiquement)
- **Refresh tokens** : 90 jours (durée standard Microsoft)
- **Cache des métadonnées** : Jusqu'à suppression manuelle ou désinstallation

### 6.2 Logs et historique
- **Fichiers de logs** : Conservation illimitée sur votre appareil
- **Limitation automatique** : Maximum 10 fichiers de logs (configurable)
- **Purge manuelle** : Vous pouvez supprimer les logs à tout moment

### 6.3 Suppression des données
Vous pouvez supprimer toutes vos données à tout moment en :
- Désinstallant l'application
- Supprimant les fichiers dans le dossier d'installation
- Révoquant les permissions dans votre compte Microsoft

## 7. Partage des données

### 7.1 Aucun partage avec des tiers
Nous ne partageons JAMAIS vos données avec :
- ❌ Des partenaires commerciaux
- ❌ Des réseaux publicitaires
- ❌ Des services d'analyse tiers
- ❌ Des gouvernements (sauf obligation légale)

### 7.2 Prestataires techniques
Aucun prestataire externe n'a accès à vos données car :
- L'application fonctionne entièrement en local
- Aucun service cloud tiers n'est utilisé
- Aucune transmission de données vers l'extérieur

### 7.3 Obligations légales
En cas d'obligation légale impérative, nous pourrions être contraints de :
- Fournir des informations sur l'utilisation de l'application
- Coopérer avec les autorités judiciaires
- **Limitation** : Nous n'avons accès qu'aux informations publiques (pas à vos données personnelles)

## 8. Sécurité des données

### 8.1 Mesures techniques
- **Chiffrement des tokens** : Stockage sécurisé des credentials
- **HTTPS exclusivement** : Toutes les communications avec Microsoft
- **Isolation des processus** : Séparation des threads de traitement
- **Validation des entrées** : Contrôle de tous les paramètres utilisateur

### 8.2 Mesures organisationnelles
- **Développement sécurisé** : Code source auditable (open source)
- **Mise à jour régulière** : Corrections de sécurité appliquées rapidement
- **Documentation complète** : Transparence sur le fonctionnement
- **Support réactif** : Réponse rapide aux signalements de sécurité

### 8.3 Recommandations utilisateur
Pour maximiser votre sécurité :
- ✅ Maintenez votre système d'exploitation à jour
- ✅ Utilisez un antivirus à jour
- ✅ Ne partagez jamais vos identifiants Microsoft
- ✅ Révoquezles permissions si vous cessez d'utiliser l'application

## 9. Vos droits (RGPD)

### 9.1 Droit d'accès (Art. 15)
Vous pouvez :
- Consulter toutes vos données stockées localement
- Examiner les fichiers de logs à tout moment
- Vérifier les permissions accordées dans votre compte Microsoft

### 9.2 Droit de rectification (Art. 16)
Vous pouvez :
- Modifier vos informations de profil Microsoft directement
- Corriger les métadonnées de fichiers dans OneDrive
- Régénérer les hash perceptuels en relançant l'analyse

### 9.3 Droit à l'effacement (Art. 17)
Vous pouvez :
- Supprimer tous les fichiers de données locaux
- Désinstaller complètement l'application
- Révoquer toutes les permissions Microsoft Graph

### 9.4 Droit à la portabilité (Art. 20)
Vous pouvez :
- Exporter la base de données SQLite (format standard)
- Sauvegarder vos fichiers de configuration
- Utiliser les données avec d'autres applications compatibles

### 9.5 Droit d'opposition (Art. 21)
Vous pouvez :
- Désactiver la détection visuelle (hash perceptuels)
- Refuser la journalisation détaillée
- Cesser l'utilisation à tout moment

### 9.6 Exercice de vos droits
Pour exercer vos droits :
- **Actions automatiques** : La plupart des actions sont disponibles dans l'interface
- **Support** : Contactez-nous à contact@duplicatefinder.fr
- **Délai de réponse** : 30 jours maximum (généralement sous 72h)

## 10. Transferts internationaux

### 10.1 Localisation des données
- **Vos données** : Stockées exclusivement sur votre appareil (votre juridiction)
- **Authentification Microsoft** : Serveurs Microsoft selon leur politique
- **Aucun autre transfert** : Pas de transmission vers d'autres pays

### 10.2 Protection lors des transferts
- **Chiffrement TLS** : Toutes les communications avec Microsoft
- **OAuth2 standard** : Protocole sécurisé reconnu mondialement
- **Minimisation** : Seules les données strictement nécessaires sont échangées

## 11. Cookies et technologies similaires

### 11.1 L'application n'utilise PAS :
- ❌ Cookies de navigation
- ❌ Pixels de tracking
- ❌ Analytics web
- ❌ Publicités ciblées

### 11.2 Stockage local uniquement :
- ✅ Fichiers de configuration
- ✅ Cache des métadonnées
- ✅ Tokens d'authentification
- ✅ Préférences utilisateur

## 12. Modifications de cette déclaration

### 12.1 Notification des changements
En cas de modification substantielle :
- **Préavis** : 30 jours avant mise en application
- **Notification** : Via l'interface de l'application
- **Version archivée** : Anciennes versions disponibles sur demande

### 12.2 Changements mineurs
Pour les corrections mineures :
- **Mise à jour immédiate** : Corrections d'erreurs ou clarifications
- **Historique disponible** : Versions précédentes sur demande
- **Numérotation** : Chaque version est datée et numérotée

## 13. Contact et réclamations

### 13.1 Délégué à la protection des données (DPO)
Pour les questions spécifiques RGPD :
- Email : dpo@duplicatefinder.fr
- Ou : contact@duplicatefinder.fr (marqué "RGPD")

### 13.2 Autorité de contrôle
Vous avez le droit de déposer une réclamation auprès de la CNIL :
- **Site web** : https://www.cnil.fr
- **Téléphone** : 01 53 73 22 22
- **Adresse** : 3 Place de Fontenoy, 75007 Paris

### 13.3 Résolution amiable
Nous nous engageons à :
- **Réponse rapide** : Sous 72h pour les questions urgentes
- **Médiation** : Recherche de solutions amiables
- **Transparence** : Communication claire sur nos pratiques

## 14. Dispositions spéciales

### 14.1 Mineurs
- **Âge minimum** : 16 ans (ou autorisation parentale)
- **Protection renforcée** : Aucune collecte de données pour les mineurs
- **Contrôle parental** : Interface claire pour les parents

### 14.2 Données sensibles
L'application peut traiter indirectement :
- **Photos personnelles** : Métadonnées uniquement, pas le contenu
- **Données biométriques** : Hash perceptuels (non identificateurs personnellement)
- **Protection** : Stockage local exclusivement

### 14.3 Conformité sectorielle
Conformité avec :
- **RGPD** : Règlement européen sur la protection des données
- **Loi Informatique et Libertés** : Réglementation française
- **Microsoft Graph ToS** : Conditions d'utilisation Microsoft

---

## Résumé en langage simple

**En résumé, OneDrive Duplicate Finder :**

✅ **Respecte votre vie privée** : Toutes vos données restent sur votre appareil
✅ **Sécurise vos informations** : Chiffrement et protocoles sécurisés
✅ **Vous donne le contrôle** : Vous pouvez tout supprimer à tout moment
✅ **Est transparent** : Code source ouvert et documentation complète
✅ **Respecte vos droits** : Conformité RGPD complète

❌ **N'espionnent pas** : Aucun tracking, analytics ou télémétrie
❌ **Ne vend pas vos données** : Aucun partenaire commercial
❌ **N'accède pas au contenu** : Seules les métadonnées sont utilisées

---

**Pour toute question sur cette déclaration de confidentialité, contactez-nous à contact@duplicatefinder.fr**

---

*Version 1.0 - Juillet 2025*
*Prochaine révision prévue : Juillet 2026*
