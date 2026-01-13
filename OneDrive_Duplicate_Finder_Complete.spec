# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collecte automatique des dépendances
datas = []
binaries = []
hiddenimports = []

# ====== COLLECTE SPÉCIFIQUE POUR IMAGEHASH ET DÉPENDANCES ======
print('Collecte des dépendances imagehash...')
tmp_ret = collect_all('imagehash')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

print('Collecte des dépendances numpy...')
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

print('Collecte des dépendances PIL/Pillow...')
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

print('Collecte des dépendances PyQt5...')
tmp_ret = collect_all('PyQt5')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

print('Collecte des dépendances requests...')
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

print('Collecte des dépendances scipy (si présent)...')
try:
    tmp_ret = collect_all('scipy')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass

print('Collecte des dépendances matplotlib (si présent)...')
try:
    tmp_ret = collect_all('matplotlib')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass

print('Collecte des dépendances MSAL...')
try:
    tmp_ret = collect_all('msal')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass

print('Collecte des dépendances Flask...')
try:
    tmp_ret = collect_all('flask')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass

print('Collecte des dépendances cryptography...')
try:
    tmp_ret = collect_all('cryptography')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass

# ====== FICHIERS DE CONFIGURATION ET CONTENU ======
print('Ajout des fichiers de configuration et contenu...')

# Fichier de configuration principal  
if os.path.exists('config.cfg'):
    datas += [('config.cfg', '.')]

# Dossier content avec toutes les images
if os.path.exists('content'):
    for file in os.listdir('content'):
        if os.path.isfile(os.path.join('content', file)):
            datas += [(os.path.join('content', file), 'content')]

# Tous les modules Python du projet
project_modules = [
    'style.py',
    'widgets.py'
]

for module in project_modules:
    if os.path.exists(module):
        datas += [(module, '.')]

# Dossier fonctions complet
if os.path.exists('fonctions'):
    for file in os.listdir('fonctions'):
        if file.endswith('.py') and not file.startswith('__'):
            datas += [(os.path.join('fonctions', file), 'fonctions')]

# ====== IMPORTS CACHÉS COMPLETS ======
hiddenimports += [
    # Core imagehash et numpy
    'imagehash',
    'imagehash.hashes',
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    'numpy.fft',
    'numpy._globals',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.linalg.lapack_lite',
    'numpy.linalg._umath_linalg',
    
    # PIL/Pillow complet
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    'PIL.ImageEnhance',
    'PIL.ImageOps',
    'PIL._tkinter_finder',
    'PIL.report',
    'PIL.features',
    
    # Formats d'images PIL
    'PIL.JpegImagePlugin', 
    'PIL.PngImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.TiffImagePlugin',
    'PIL.WebPImagePlugin',
    'PIL.IcoImagePlugin',
    
    # PyQt5 complet
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.Qt',
    'PyQt5.sip',
    
    # Requests et dépendances
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'requests.structures',
    'requests.utils',
    'urllib3',
    'urllib3.connection',
    'urllib3.connectionpool',
    'urllib3.response',
    'urllib3.poolmanager',
    'certifi',
    'charset_normalizer',
    'idna',
    
    # Standard library nécessaire
    'sqlite3',
    'threading',
    'webbrowser',
    'json',
    'time',
    'os',
    'sys',
    'io',
    'itertools',
    'logging',
    'configparser',
    
    # Modules du projet
    'style',
    'widgets',
    'fonctions.graph',
    'fonctions.logger', 
    'fonctions.token_manager',
    'fonctions.server',
    'fonctions.sql',
    'fonctions.config',
    'fonctions.token_security',
    'fonctions.threads',
    'fonctions.doublons',
    'fonctions.compte_photos',
    
    # Cryptographie (pour les tokens)
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.backends.openssl',
    
    # MSAL (Microsoft Authentication Library)
    'msal',
    'msal.application',
    'msal.oauth2cli',
    'msal.authority',
    'msal.token_cache',
    
    # Flask (pour le serveur d'authentification)
    'flask',
    'flask.app',
    'flask.helpers',
    'flask.wrappers',
    'werkzeug',
    'werkzeug.serving',
    'werkzeug.utils',
]

# ====== EXCLUSIONS (pour réduire la taille) ======
excludes = [
    'tkinter',
    'matplotlib.tests',
    'numpy.tests', 
    'scipy.tests',
    'PIL.tests',
    'test',
    'tests',
    '_pytest',
    'pytest',
]

# ====== CONFIGURATION PYINSTALLER ======
a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# Supprimer les doublons
a.datas = list(set(a.datas))

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OneDrive_Duplicate_Finder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Interface graphique
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='content/onedrive_logo.png' if os.path.exists('content/onedrive_logo.png') else None,
    version_file=None,
)

print('Configuration PyInstaller terminée !')
print('Total de fichiers de données:', len(a.datas))
print('Total d imports cachés:', len(hiddenimports))

