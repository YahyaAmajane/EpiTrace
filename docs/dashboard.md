# 🖥️ Guide du Centre de Commandement Streamlit

L'interface utilisateur d'Epi-Trace a été développée avec Streamlit en adoptant une charte graphique premium de type "salle de contrôle tactique" (fond sombre `#04070F`, polices *Syne* / *Space Grotesk* / *JetBrains Mono*, graphiques Plotly sombres).

L'application est structurée en **5 onglets opérationnels** destinés aux décideurs hospitaliers et cliniciens.

---

## 📊 1. Tableau de Bord Tactique

Cet onglet offre une vue globale instantanée de l'état sanitaire de la région Île-de-France :

* **7 Indicateurs Clés (KPIs) en temps réel** : Incidence présente, Prévision à J+7, Température, Humidité, et les volumes de recherche Google pour les symptômes *Toux*, *Grippe* et *Fièvre*.
* **Niveau d'Alerte Tactique** : Affiche le niveau d'alerte ORSAN calculé sur les percentiles de distribution réels de 2021 à 2026 :
    * 🟢 **VEILLE** : Incidence $\lt 14\,206$ cas (Percentile 50).
    * 🟡 **PRÉ-ALERTE** : Incidence $\lt 20\,076$ cas (Percentile 75).
    * 🟠 **PLAN BLANC** : Incidence $\lt 26\,866$ cas (Percentile 85).
    * 🔴 **ALERTE ROUGE** : Incidence $\ge 26\,866$ cas (Percentile 85+).
* **Radar des Signaux exogènes** : Visualisation multidimensionnelle de la force des signaux précurseurs de la semaine.

---

## 🔮 2. Moteur de Prévision

Cet onglet permet à l'utilisateur de simuler deux situations de terrain :

* **Mode Standard (Forecasting Pur)** : Utilisé lorsque le réseau Sentinelles a déjà publié ses chiffres hebdomadaires. L'incidence réelle $S_0$ alimente directement le modèle BiLSTM pour prédire la semaine suivante ($S_{+1}$).
* **Mode Urgence (Cascade d'IA)** : Activé le lundi matin en l'absence de données cliniques officielles. L'incidence actuelle $S_0$ est masquée (`■■■■`). Le Nowcaster MLP l'estime, puis l'injecte automatiquement dans le tenseur d'entrée pour que le Forecaster BiLSTM puisse prédire $S_{+1}$.
* **Panel de Transparence Algorithmique** : En mode urgence, l'application affiche une comparaison détaillée entre l'estimation du Nowcaster et la vérité clinique (dès qu'elle est publiée a posteriori) en affichant l'écart d'erreur et un cône d'incertitude de $\pm$RMSE ($\pm$4 116 cas).

---

## 📈 3. Signaux Précurseurs (Infodémiologie)

Cet onglet regroupe les outils de diagnostic visuel des corrélations :

* **Vue 1 : Superposition Temporelle** : Graphique double axe Y affichant l'évolution des recherches Google Trends (Toux, Grippe, Fièvre) superposées aux courbes réelles des malades. On y observe la synchronisation et la force de précurseur des signaux web.
* **Vue 2 : Scatter Plot Température × Humidité** : Graphique en nuage de points projetant l'incidence clinique selon le climat local, où la couleur des points représente l'humidité et leur taille le volume de recherche "Toux".
* **Vue 3 : Heatmap de Corrélation** : Matrice 7×7 affichant les coefficients de Pearson calculés sur le cube OLAP de 277 semaines d'historique.

---

## 🤖 4. Agent IA Décisionnel (RAG)

Cet onglet intègre un agent conversationnel autonome chargé de rédiger le rapport officiel de crise :

* **Base de Connaissances** : L'agent charge et indexe le document officiel du Ministère de la Santé : `docs/protocole_orsan_reb.md` (Plan Blanc, plan Orsan, organisation de crise).
* **Rapport de Prévision** : Les prédictions d'incidence du modèle BiLSTM et le niveau d'alerte Orsan calculé sont injectés dans le contexte du modèle LLM (**Gemini 2.5 Flash**).
* **Garantie anti-hallucination** : Le prompt système interdit formellement au modèle d'inventer des procédures médicales ou de citer des protocoles absents de la base de connaissances. L'agent rédige un bulletin structuré (🏥 *Directives Hôpitaux*, 💊 *Pharmacies*, 🩺 *Médecine de Ville*) avec un bouton pour le télécharger en format HTML.

---

## 🎛️ 5. Simulateur What-If (Scénarios de Crise)

Un outil d'explicabilité par l'interaction pour les cliniciens et le jury :

* **7 Sliders interactifs** : Permettent de modifier manuellement la température, l'humidité, les indices Google Trends (Toux, Grippe, Fièvre), le ratio de vacances scolaires, et de simuler une incidence de départ.
* **Prédiction en temps réel** : À chaque déplacement de slider, le modèle BiLSTM ré-exécute son inférence instantanément et trace une courbe comparative : *Scénario Réel* vs *Scénario Simulé*.
* **Interprète Automatique** : L'application analyse la différence de courbe et affiche un diagnostic textuel de couleur dynamique :
    * 🔴 **AGGRAVATION** : Hausse marquée de l'incidence prévue.
    * 🟢 **AMÉLIORATION** : Baisse significative de la charge prévue.
    * 🔵 **NEUTRE** : Variation négligeable ($\lt 500$ cas).
