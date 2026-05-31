# 🔌 Référence API Python

Cette page documente automatiquement l'interface de programmation d'Epi-Trace. Elle est extraite directement des docstrings du code source à l'aide de l'extension `mkdocstrings`.

---

## 🖥️ Module Utilitaire de l'Application (`app/app_utils.py`)

Ce module gère le chargement en cache des modèles de Deep Learning (Nowcaster & Forecaster), les transformations de scalers et le calcul des percentiles épidémiques pour les alertes.

::: app.app_utils
    options:
      show_source: true
      show_root_heading: true

---

## 🤖 Module de l'Agent Décisionnel RAG (`src/agent_llm.py`)

Ce module configure l'agent RAG utilisant Gemini 2.5 Flash pour analyser les prédictions d'incidence sous le protocole ORSAN REB du Ministère de la Santé.

::: src.agent_llm
    options:
      show_source: true
      show_root_heading: true

---

## 🔄 Pipeline ETL Live (`build_live_cube.py`)

Ce script orchestre en direct l'interrogation des API (SentiWeb, Open-Meteo et SerpAPI) et réalise l'alignement temporel des données pour générer le cube live hebdomadaire.

::: build_live_cube
    options:
      show_source: true
      show_root_heading: true
