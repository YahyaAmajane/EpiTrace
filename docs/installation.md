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

### 🟢 Option A : Exécution en mode Démo (Recommandé pour un test rapide)
Le projet est livré avec un jeu de données pré-compilé et aligné jusqu'au présent : `data/traitees/epitrace_cube_live.csv`. 

Dans ce mode, l'application fonctionne **directement sans requérir de clés d'API tierces pour la récolte des données** :
```bash
streamlit run app/app.py
```
*Note : L'onglet "Agent IA" aura tout de même besoin d'une clé `GEMINI_API_KEY` dans le fichier `.env` pour générer des bulletins.*

---

### 🔴 Option B : Reconstruction du Cube en temps réel (ETL Complet)
Si vous souhaitez simuler un rafraîchissement complet en direct le lundi matin et interroger les sources externes :

1. Assurez-vous d'avoir configuré votre `SERPAPI_KEY` dans le fichier `.env`.
2. Lancez le script d'orchestration ETL :
   ```bash
   python build_live_cube.py
   ```
   Ce script va :
   * Télécharger les dernières observations épidémiques locales.
   * Interroger l'API **Open-Meteo** pour récupérer les données horaires de température et d'humidité récentes (latence 0j).
   * Appeler **SerpAPI** pour scraper les indices de recherche sur Google (Toux, Grippe, Fièvre).
   * Aligner et agréger le tout au format hebdomadaire ISO pour générer un nouveau fichier `epitrace_cube_live.csv` à jour.
3. Lancez le Dashboard pour observer les prévisions actualisées par la cascade d'IA :
   ```bash
   streamlit run app/app.py
   ```

L'interface web sera alors accessible à l'adresse : `http://localhost:8501`.
