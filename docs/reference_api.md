# 🔌 Référence de l'API Python & Modèles d'IA

Cette section contient la documentation technique des modules Python d'Epi-Trace, le schéma de données du cube OLAP et les fiches techniques des modèles de Deep Learning.

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

Les documentations suivantes sont extraites directement des docstrings de votre code via `mkdocstrings`.

### Module Utilitaire de l'Application (`app/app_utils.py`)
Ce module gère le chargement en cache des modèles de Deep Learning (Nowcaster & Forecaster), les transformations de scalers et le calcul des percentiles épidémiques pour les alertes.

::: app.app_utils
    options:
      show_source: true
      show_root_heading: true

---

### Module de l'Agent Décisionnel RAG (`src/agent_llm.py`)
Ce module configure l'agent RAG utilisant Gemini 2.5 Flash pour analyser les prédictions d'incidence sous le protocole ORSAN REB du Ministère de la Santé.

::: src.agent_llm
    options:
      show_source: true
      show_root_heading: true

---

### Pipeline ETL Live (`build_live_cube.py`)
Ce script orchestre en direct l'interrogation des API (SentiWeb, Open-Meteo et SerpAPI) et réalise l'alignement temporel des données pour générer le cube live hebdomadaire.

::: build_live_cube
    options:
      show_source: true
      show_root_heading: true

---

### Module d'Extraction Météo (`src/extract_meteo.py`)
Ce module extrait les archives climatiques horaires et récentes (température, humidité, précipitations, vent) depuis l'API Open-Meteo et les agrège localement.

::: src.extract_meteo
    options:
      show_source: true
      show_root_heading: true

---

### Module de Nettoyage Clinique (`src/extract_sentinelles.py`)
Ce module importe la vérité terrain hebdomadaire du Réseau Sentinelles, filtre géographiquement pour l'Île-de-France et formate les cas d'incidences.

::: src.extract_sentinelles
    options:
      show_source: true
      show_root_heading: true

---

### Module d'Extraction Google Trends (`src/extract_trends.py`)
Ce module gère le scraping et l'extraction des volumes de recherche Google Trends via l'API SerpAPI en utilisant un découpage par chunks temporels pour forcer l'agrégation hebdomadaire stable.

::: src.extract_trends
    options:
      show_source: true
      show_root_heading: true
