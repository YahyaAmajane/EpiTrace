# ⚙️ Guide d'Installation et d'Exécution

Suivez les instructions suivantes pour déployer Epi-Trace sur votre machine locale et tester ses fonctionnalités.

---

## 📋 Prérequis

Pour exécuter ce projet, vous devez disposer de :
* **Python 3.9 à 3.11** d'installé.
* Une clé d'API **SerpAPI** (optionnelle, uniquement si vous souhaitez mettre à jour les données Google Trends en direct).
* Une clé d'API **Google Gemini** (nécessaire pour exécuter l'Agent de décision RAG).

---

## 🛠️ Installation pas-à-pas

### 1. Clonage du dépôt Git
Clonez le dépôt depuis GitHub et déplacez-vous dans le répertoire du projet :
```bash
git clone https://github.com/YahyaAmajane/EpiTrace.git
cd EpiTrace
```

### 2. Création et activation de l'environnement virtuel
Il est fortement recommandé de créer un environnement virtuel pour éviter les conflits de dépendances :

Sur **Windows (PowerShell)** :
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Sur **Linux / macOS** :
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installation des dépendances
Installez les packages nécessaires répertoriés dans le fichier `requirements.txt` :
```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement (`.env`)
À la racine du projet, créez un fichier nommé `.env` et ajoutez vos clés secrètes :
```env
SERPAPI_KEY=votre_cle_serpapi_ici
GEMINI_API_KEY=votre_cle_gemini_ici
```

---

## 🚀 Lancement & Modes d'Exécution

Deux options s'offrent à vous pour faire tourner et tester le système :

### 🟢 Option A : Exécution en mode Démo (Option la plus rapide — Idéal Jury)
C'est l'option recommandée pour une démonstration immédiate et sans tracas. Le projet est pré-configuré avec un cube de données OLAP extrait et nettoyé : `data/traitees/epitrace_cube_live.csv`.
* **Dernière prévision** : Ce fichier contient l'historique complet et permet de lancer des prédictions directes pour la **première semaine de juin 2026** (semaine 23 de 2026).
* **Lancement** : Dans ce mode, aucune clé d'API tierce n'est requise pour le cube de données. Lancez simplement l'application Streamlit :
  ```bash
  streamlit run app/app.py
  ```
  *(Note : L'onglet "Agent IA" aura tout de même besoin d'une clé `GEMINI_API_KEY` dans le fichier `.env` pour pouvoir générer ses rapports).*

---

### 🔴 Option B : Reconstruction du Cube en temps réel (ETL Complet & Dates Personnalisées)
Si vous souhaitez actualiser la base de données en direct ou cibler une date de fin spécifique :

1. **Clés d'APIs** : Assurez-vous d'avoir configuré vos clés `SERPAPI_KEY` et `GEMINI_API_KEY` dans votre fichier `.env`.
2. **Télécharger la Vérité Terrain** :
   - Allez sur le site officiel du Réseau Sentinelles : [sentiweb.fr](https://www.sentiweb.fr/).
   - Téléchargez le fichier de données historiques régionales pour la grippe (ou les affections respiratoires aiguës).
   - Placez le fichier CSV téléchargé dans le dossier `data/brutes/` (par défaut, le script cherche le fichier nommé `inc-25-RDD-ds2.csv`).
3. **Exécuter le pipeline ETL** :
   - Vous pouvez ouvrir le script `build_live_cube.py` et configurer la date de fin souhaitée dans les paramètres d'appel de fin (ex: fin 2026 ou autre).
   - Lancez la reconstruction du cube :
     ```bash
     python build_live_cube.py
     ```
     Ce script va automatiquement :
     - Lire et filtrer la vérité terrain locale depuis le fichier Sentinelles.
     - Appeler l'API **Open-Meteo** pour extraire les données climatiques (températures, humidité) correspondantes.
     - Scraper les volumes de recherche sur **Google Trends** via SerpAPI pour les mots-clés de symptômes.
     - Aligner temporellement et fusionner toutes les sources en un cube OLAP propre.
4. **Lancement du Dashboard** :
   ```bash
   streamlit run app/app.py
   ```

L'interface web sera alors accessible à l'adresse : `http://localhost:8501`.
