# Chess.AI : Projet Math-Info L1 (Arbres de Stratégie)



Ce document sert à la fois de `README.md` pour le projet et de brouillon principal pour le **Rapport** et la **Soutenance**, conformément au PDF d'évaluation (`projet.pdf`).

![Aperçu de ChessAI](logo.png)

---

## 1. Manuel d'utilisation (Pour le README et le Rapport)

Cette section explique comment installer et lancer le projet.

### Installation (Requis)

Le projet nécessite des dépendances système (Graphviz) et des bibliothèques Python.

#### Pour macOS (Recommandé)

**Étape 1 : Installer l'outil système Graphviz**

    La visualisation de l'arbre (`pygraphviz`) a besoin de cet outil. Le plus simple est d'utiliser [Homebrew](https://brew.sh/).

    ```bash
    # Si vous n'avez pas Homebrew, installez-le d'abord
    /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"

    # Ensuite, installez Graphviz
    brew install graphviz


Étape 2 : Installer les bibliothèques Python

    # 1. Allez dans le dossier du projet
    cd chemin/vers/votre/projet

    # 2. Créez l'environnement virtuel
    python3 -m venv env

    # 3. Activez l'environnement
    source env/bin/activate

    # 4. Installez les bibliothèques Python
    pip install ttkbootstrap matplotlib networkx

    # 5. Installez pygraphviz (commande spéciale pour Mac)
    CPPFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install pygraphviz



                                                           Pour Windows
Étape 1 : Installer l'outil système Graphviz

    Allez sur le site officiel de Graphviz : https://graphviz.org/download/

    Téléchargez et installez le programme.

    IMPORTANT : Pendant l'installation, cochez la case "Add Graphviz to the system PATH".

Étape 2 : Installer les bibliothèques Python

    # 1. Ouvrez un terminal (cmd ou PowerShell) dans le dossier du projet

    # 2. Créez l'environnement virtuel
    python -m venv env

    # 3. Activez l'environnement
    .\env\Scripts\activate

    # 4. Installez les bibliothèques Python
    pip install ttkbootstrap matplotlib networkx pygraphviz

(Note : Si pip install pygraphviz échoue sur Windows, c'est que l'étape 1 a échoué. Assurez-vous que Graphviz est bien ajouté au PATH.)

##Lancement du logiciel
    # 1. Activez l'environnement
    # Sur Mac:
    source env/bin/activate
    # Sur Windows:
    .\env\Scripts\activate

    # 2. Lancez le jeu
    python main.py

