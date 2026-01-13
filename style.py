couleur_fond = "#1ea2e7"
couleur_secondaire = "#046abc"
couleur_tertiaire = "#1481d7"
couleur_texte = "#1e2447"

cssBouton = f"""
    QPushButton {{
        background-color: {couleur_secondaire};
        color: {couleur_texte};
        border: none;
        border-radius: 18px;
        padding: 8px 20px;
        font-size: 18px;
        font-weight: 600;
        margin: 2px;
    }}

    QPushButton:hover {{
        background-color: "{couleur_tertiaire}";
    }}

    QPushButton:pressed {{
        background-color: #4fa3d1;
    }}
"""

cssBoutonAcheve = f"""
    background-color: green; 
    color: {couleur_texte};
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 600;
    margin: 2px;
"""

cssBoutonErreur = f"""
    background-color: red; 
    color: {couleur_texte};
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 600;
    margin: 4px;
"""

cssBoutonDesactive = f"""
    background-color: #7F8C99; 
    color: {couleur_texte};
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-size: 18px;
    font-weight: 600;
    margin: 42pxpx;
"""

cssTitre = f"""
    margin-top: 10px;
    padding: 30px; 
    color: {couleur_texte};
    font-size: 80px;
    font-weight: bold;
    padding: 8px 20px;
    border-radius: 12px;
    qproperty-alignment: AlignCenter;
"""

cssSousTitre = f"""
    font-size: 20px; 
    color: {couleur_texte}; 
    margin-top: 5px; 
"""

cssPath = f"""
    font-size: 20px; 
    color: {couleur_texte}; 
    border: None;
    font-weight: bold;
"""

cssChiffre = f"""
        background-color: {couleur_tertiaire};
        color: {couleur_texte};
        border: solid black 5px;
        border-radius: 18px;
        padding: 8px 20px;
        font-size: 18px;
        font-weight: bold;
        margin: 2px;
"""

cssChiffreActive = f"""
        background-color: {couleur_fond};
        color: {couleur_texte};
        border: solid black 5px;
        border-radius: 18px;
        padding: 8px 20px;
        font-size: 18px;
        font-weight: bold;
        margin: 2px;
"""

cssTexte = f"""
    font-size: 15px; 
    color: {couleur_texte}; 
    margin-top: 10px; 
    border: None;
"""

cssUser = f"""
    font-size: 15px; 
    color: {couleur_texte}; 
    margin-top: 10px; 
    qproperty-alignment: AlignCenter;
"""

cssZoneTexte = f"""
    QTextEdit {{
        background-color: {couleur_fond};
        color: {couleur_texte};
        border: 5px solid black;
        border-radius: 10px;
        padding: 8px 20px;
        font-size: 20px;
        margin-top: 5px;
        margin-right: 5px;
        margin-left: 5px;
        margin-bottom: 5px;
        font-family: Arial;
    }}
"""

cssScrollArea = f"""    
    QScrollArea {{
        background-color: {couleur_fond};
        color: {couleur_texte};
        border: 5px solid black;
        border-radius: 10px;
        font-size: 15px;
        font-family: Arial;
        padding: 10px;
        margin-top: 5px;
        margin-right: 5px;
        margin-left: 5px;
        margin-bottom: 5px;
    }}
"""

cssParametreTitre = f"""
    font-size: 40px; 
    color: {couleur_texte}; 
    font-weight: bold;
    margin-top: 5px; 
    qproperty-alignment: AlignCenter;
"""

cssPixMap = f"""
    background-color: rgba(0, 0, 0, 0);
    border: 5px solid black;
    border-radius: 10px;
    padding: 10px;
    margin-top: 5px;
    margin-right: 5px;
    margin-left: 5px;
    margin-bottom: 5px;
"""

cssSpinBox = f"""
    QSpinBox {{
        background-color: {couleur_fond};
        color: {couleur_texte};
        border: 2px solid {couleur_texte};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 14px;
    }}

    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {couleur_secondaire};
        border: none;
        width: 16px;
        subcontrol-origin: border;
    }}

    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {couleur_tertiaire};
    }}

    QSpinBox::up-arrow, QSpinBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
    }}
"""

cssLoupe = f"""
    QPushButton {{
        background-color: transparent;
        border: none;
        font-size: 18px;
        padding: 2px;
    }}
    
    QPushButton:hover {{
        font-size: 22px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 1px;
    }}
"""

cssDoublonContainer = f"""
    QWidget {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin: 2px;
        padding: 5px;
    }}
"""