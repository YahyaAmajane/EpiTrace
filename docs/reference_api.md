# 🔌 Référence de l'API Python & Modèles d'IA

Cette section contient la documentation technique détaillée de l'ensemble des modules Python d'Epi-Trace, le schéma du cube OLAP et les fiches techniques des modèles de Deep Learning.

---

## 📊 1. Schéma de Données du Cube OLAP

Le cube de données final (`data/traitees/epitrace_cube_live.csv`) est un cube OLAP à grain hebdomadaire alignant temporellement la vérité clinique avec les signaux exogènes numériques et physiques :

| Colonne | Type | Source | Description Sémantique |
|:---|:---|:---|:---|
| **date** | `datetime` | Calendrier | Lundi de la semaine épidémiologique d'observation (Norme ISO). |
| **inc** | `int` | Sentiweb (Santé Publique France) | Nombre estimé de cas de grippe/taux régionaux pour la semaine. |
| **temp** | `float` | Open-Meteo API | Température moyenne hebdomadaire observée à 2 mètres (en °C). |
| **humidity** | `float` | Open-Meteo API | Humidité relative moyenne hebdomadaire observée (en %). |
| **Topic_Grippe** | `int` | Google Trends (via SerpAPI) | Volume de recherche relatif (0-100) pour le topic grippal régional. |
| **Topic_Toux** | `int` | Google Trends (via SerpAPI) | Volume de recherche relatif (0-100) pour le topic de la toux régionale. |
| **Topic_Fievre** | `int` | Google Trends (via SerpAPI) | Volume de recherche relatif (0-100) pour le topic fébrile régional. |
| **vacances_ratio** | `float` | Ministère de l'Éducation Nationale | Ratio continu (0.0 à 1.0) mesurant la part de la semaine passée en vacances scolaires pour la zone de l'Île-de-France. |

---

## 🧠 2. Fiches Techniques des Modèles d'IA

### Nowcaster (MLP Delta)
* **Objectif** : Estimer l'incidence clinique de la semaine en cours ($S_0$) en temps réel à J+0, sans données cliniques de la semaine en cours, en s'appuyant sur l'inertie passée et les signaux temps réel.
* **Algorithme** : Perceptron Multicouche (MLP) entraîné sur les deltas.
* **Tenseur d'entrée** : Vecteur 1D de taille 18 (11 semaines passées d'incidences, plus les exogènes climat, trends et vacances de la semaine en cours).
* **Architecture** :
    - Couche Dense 1 : 64 neurones, activation ReLU, régularisation L2.
    - Couche Dense 2 : 32 neurones, activation ReLU.
    - Couche Dense de sortie : 1 neurone, activation linéaire (prédit $\Delta$).
* **Entraînement** : Optimiseur Adam, loss Mean Squared Error (MSE), batch size = 16, early stopping (patience = 15).

### Forecaster (BiLSTM)
* **Objectif** : Prédire la charge hospitalière/l'incidence de la semaine prochaine ($S_{+1}$) à J+7.
* **Algorithme** : Réseau de neurones récurrents bidirectionnel (BiLSTM) adapté aux séries temporelles asymétriques.
* **Tenseur d'entrée** : Tenseur 3D de dimension `(batch_size, 12, 7)` représentant une fenêtre glissante de 12 semaines et 7 features (l'incidence complétée en production par le Nowcaster, la météo, les trends et le ratio de vacances).
* **Architecture** :
    - Couche Bidirectionnelle (LSTM) : 64 neurones, return_sequences=False.
    - Couche de régularisation Dropout : Taux de 0.2 (anti-overfitting).
    - Couche Dense de sortie : 1 neurone, activation linéaire (prédit l'incidence à $S_{+1}$).
* **Entraînement** : Optimiseur Adam avec régulateur de learning rate (`ReduceLROnPlateau`), loss MSE, batch size = 32, early stopping (patience = 10).

---

## 💻 3. Documentation des Modules Python

### 🔄 Pipeline ETL d'Orchestration (`build_live_cube.py`)

Ce script coordonne l'extraction, le traitement et la fusion de toutes les sources de données (clinique, météo, trends) pour générer le cube OLAP en direct.

#### `process_sentinelles`
```python
def process_sentinelles(nom_fichier="sentinelles_latest.csv", fenetre_semaines=60):
```
* **Description** : Lit le fichier brut du Réseau Sentinelles, filtre uniquement la région Île-de-France (Code INSEE `11`), convertit la semaine ISO en date et extrait les X dernières semaines.
* **Paramètres** :
    - `nom_fichier` (*str*) : Nom du fichier Sentinelles dans `data/brutes/`.
    - `fenetre_semaines` (*int*) : Nombre de semaines d'historique à conserver (par défaut `60`).
* **Retour** : Un tuple `(df_recent, date_min, date_max)` contenant le DataFrame des données nettoyées et les bornes temporelles.

#### `process_meteo`
```python
def process_meteo(date_min, date_max):
```
* **Description** : Interroge l'API Open-Meteo pour récupérer l'historique horaire de température et d'humidité sur les coordonnées géographiques de Paris de `date_min` à `date_max + 7 jours`, puis agrège ces données par moyenne hebdomadaire.
* **Paramètres** :
    - `date_min` (*datetime*) : Date de début de la fenêtre d'observation.
    - `date_max` (*datetime*) : Date de fin de la fenêtre d'observation.
* **Retour** : Un DataFrame Pandas contenant les colonnes `date`, `temperature_2m` et `relative_humidity_2m`.

#### `process_trends`
```python
def process_trends(date_min, date_max):
```
* **Description** : Récupère les données d'infodémiologie via SerpAPI pour les requêtes "toux", "grippe" et "fievre" sur la période donnée pour la région Île-de-France.
* **Paramètres** :
    - `date_min` (*datetime*) : Date de début.
    - `date_max` (*datetime*) : Date de fin.
* **Retour** : Un DataFrame Pandas contenant les tendances d'intérêt Google Trends associées.

#### `calc_ratio_vacances`
```python
def calc_ratio_vacances(date_dimanche):
```
* **Description** : Calcule la proportion de la semaine (lundi au dimanche) passée en vacances scolaires de Zone C (Île-de-France) sous forme de valeur continue $\in [0.0, 1.0]$.
* **Paramètres** :
    - `date_dimanche` (*datetime*) : Date représentant la fin de la semaine.
* **Retour** : Un `float` représentant le ratio de vacances.

---

### 🌤️ Module d'Extraction Météo (`src/extract_meteo.py`)

Ce script permet de collecter les données physiques météorologiques sur de longues périodes d'archives.

#### `fetch_open_meteo_data`
```python
def fetch_open_meteo_data(lat, lon, start_date, end_date, filename):
```
* **Description** : Envoie une requête à l'API d'archive d'Open-Meteo pour obtenir les observations horaires (température, humidité, précipitations, vitesse du vent) et enregistre le résultat au format CSV brut dans le dossier `data/brutes/`.
* **Paramètres** :
    - `lat` (*float*) : Latitude géographique (ex: `48.8566` pour Paris).
    - `lon` (*float*) : Longitude géographique (ex: `2.3522` pour Paris).
    - `start_date` (*str*) : Date de début au format `YYYY-MM-DD`.
    - `end_date` (*str*) : Date de fin au format `YYYY-MM-DD`.
    - `filename` (*str*) : Nom du fichier de sortie CSV.
* **Retour** : Un DataFrame Pandas contenant l'historique brut des conditions horaires.

---

### 🩺 Module de Nettoyage Clinique (`src/extract_sentinelles.py`)

Ce script nettoie le jeu de données épidémiologiques brutes publiées nationalement.

#### `clean_local_sentinelles_data`
```python
def clean_local_sentinelles_data(input_filename, output_filename):
```
* **Description** : Charge le fichier CSV national, extrait l'incidence épidémique de l'Île-de-France (Code INSEE `11`) et extrait uniquement les variables de semaine ISO (`week`) et le nombre de cas d'incidence (`inc`). Enregistre le fichier filtré dans `data/brutes/`.
* **Paramètres** :
    - `input_filename` (*str*) : Nom du fichier national d'entrée.
    - `output_filename` (*str*) : Nom du fichier de sortie régionalisé.
* **Retour** : `None`.

---

### 📈 Module d'Extraction Google Trends (`src/extract_trends.py`)

Ce script scrape l'intérêt de recherche Google pour un ensemble de symptômes et médicaments.

#### `fetch_aggregated_trends`
```python
def fetch_aggregated_trends(query, column_name, geo, api_key):
```
* **Description** : Interroge SerpAPI pour récupérer l'historique Google Trends d'une requête spécifique.
* **Technique Data Engineer** : Pour contourner la limite de 5 ans de Google Trends (qui basculerait les résultats en grain mensuel), le script découpe le temps en "chunks" inférieurs à 5 ans et réalise ensuite un alignement et une fusion chronologique.
* **Paramètres** :
    - `query` (*str*) : Expression recherchée (ex: `toux + sirop toux`).
    - `column_name` (*str*) : Nom de colonne à assigner dans le DataFrame final.
    - `geo` (*str*) : Code géographique régional (ex: `FR-J` pour l'Île-de-France).
    - `api_key` (*str*) : Clé SerpAPI.
* **Retour** : Un DataFrame Pandas contenant les dates et les valeurs d'intérêt associées.

#### `build_candidates_matrix`
```python
def build_candidates_matrix():
```
* **Description** : Fonction principale du module. Scrape séquentiellement 9 topics médicaux (grippe, fièvre, toux, paracétamol, etc.), applique des pauses de sécurité de 1.5 seconde pour éviter les bans d'API et fusionne le tout dans un unique CSV brut : `trends_9_topics_idf.csv`.
* **Paramètres** : Aucun.
* **Retour** : `None`.

---

### 🖥️ Module Utilitaire de l'Application (`app/app_utils.py`)

::: app.app_utils
    options:
      show_source: true
      show_root_heading: true

---

### 🤖 Module de l'Agent Décisionnel RAG (`src/agent_llm.py`)

::: src.agent_llm
    options:
      show_source: true
      show_root_heading: true
