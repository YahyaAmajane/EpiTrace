# 🏥 Bienvenue sur la Documentation d'Epi-Trace

**Epi-Trace** est un système d'aide à la décision hospitalière en temps réel conçu pour la gestion des tensions hospitalières liées aux **Infections Respiratoires Aiguës (IRA)**, prédisant la charge des urgences médicales en Île-de-France à **J+7**.

Ce projet a été réalisé par **Yahya Amajane** et **Mohamed Amine Belasri** dans le cadre de la filière **IATD-SI** (Intelligence Artificielle et Technologies des Données : Systèmes Industriels) à l'**ENSAM Meknès**.

---

## 🎯 Problématique Métier & Innovation

La veille sanitaire traditionnelle (menée par le réseau Sentinelles de l'INSERM) souffre d'une **latence de 12 jours** entre la consultation du patient et la publication officielle des données. Cette faille temporelle empêche les directeurs d'hôpitaux d'anticiper les vagues épidémiques (ex: grippe) et de planifier les ressources à l'avance.

**Epi-Trace résout ce problème** grâce à une **architecture en cascade d'IA** :
1. **Nowcasting** : Reconstruction de l'incidence actuelle ($S_0$) en temps réel (latence = 0 jour) via des signaux précurseurs (météo et requêtes Google Trends).
2. **Forecasting** : Prédiction de la charge hospitalière future ($S_{+1}$) à l'aide d'un réseau de neurones récurrents bidirectionnel (BiLSTM).

---

## 🗺️ Navigation dans la Documentation

Pour vous guider à travers les livrables du projet, la documentation est structurée comme suit :

* **[⚙️ Guide d'Installation](installation.md)** : Étapes pas-à-pas pour configurer votre environnement et lancer le projet en local (avec ou sans clés d'API).
* **[🧠 Architecture IA & Cascade](architecture.md)** : Explications détaillées sur les algorithmes (SARIMAX, Prophet, BiLSTM, MLP Delta), les métriques d'évaluation et la cascade d'estimation.
* **[🖥️ Centre de Commandement](dashboard.md)** : Guide complet sur l'application web Streamlit et ses 5 onglets opérationnels (KPIs, Simulateur, Agent RAG).
* **[🩺 Protocole RAG ORSAN](protocole_orsan_reb.md)** : Intégration du protocole d'urgence du Ministère de la Santé pour alimenter notre agent conversationnel.
* **[🔌 Référence API Python](reference_api.md)** : Documentation technique extraite directement des docstrings des scripts du projet (`app_utils.py`, `agent_llm.py`, etc.).

---

## 📊 Chiffres Clés d'Epi-Trace
* **Nowcaster ($S_0$)** : $R^2 = 0.892$ | RMSE = 2 633 cas (85% de précision sans données cliniques).
* **Forecaster ($S_{+1}$)** : $R^2 = 0.731$ | RMSE = 4 083 cas (erreur moyenne réduite de 43% par rapport à SARIMAX).
* **Rappel Alerte (Recall)** : **100%** (0 crise sanitaire majeure manquée sur le jeu de test).
* **Gain temporel** : **12 jours d'avance** sur les publications officielles du réseau Sentinelles.
