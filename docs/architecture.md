# 🧠 Architecture de l'Intelligence Artificielle

L'intelligence algorithmique d'Epi-Trace repose sur une validation statistique stricte combinée à une architecture de Deep Learning en cascade.

---

## 📊 1. Preuves Statistiques et Feature Engineering

Avant toute modélisation, chaque variable du cube a été analysée et validée dans le notebook `01_eda_et_correlation.ipynb` :

### Corrélation de Pearson (Force du signal synchrone)
* **Topic_Toux** ($r = +0.842$) et **Topic_Grippe** ($r = +0.812$) : Forte corrélation avec l'incidence clinique.
* **Température** ($r = −0.604$) : Corrélation négative marquée (le froid engendre une hausse de l'incidence).

### Causalité de Granger ($p \text{ } \lt \text{ } 0.05$)
Nous avons soumis nos séries temporelles à des tests de causalité de Granger pour vérifier si les signaux temps réel contiennent un pouvoir prédictif statistiquement significatif au-delà de l'historique de l'incidence :

* **Humidité** ($p = 0.0058$ au lag de 2 semaines) $\to$ **Causal** ✅
* **Température** ($p = 0.0185$ au lag de 4 semaines) $\to$ **Causal** ✅
* **Google Trends Grippe/Toux** ($p = 0.0242$ et $p = 0.0347$ au lag de 3 semaines) $\to$ **Causaux** ✅
* **Ratio de vacances scolaires** ($p = 0.0006$ au lag de 1 semaine) $\to$ **Causal** ✅

### Feature Engineering : Le Ratio Continu de Vacances
Les épidémies hivernales se propageant fortement par le brassage des enfants à l'école, nous avons intégré le calendrier scolaire. Plutôt qu'une variable binaire (0 ou 1) trop abrupte pour la descente de gradient, nous avons conçu un **ratio continu de vacances scolaires** $\in [0.0, 1.0]$. 
Une analyse par régression OLS a prouvé sa significativité absolue ($p = 0.00015$) avec un coefficient de **-6 254**, démontrant que le passage en vacances réduit l'incidence régionale de plus de 6 250 cas par semaine.

---

## ⚙️ 2. Évolution Algorithmique & Benchmark

Trois architectures de complexité croissante ont été entraînées et évaluées sur le jeu de test chronologique (Hiver 2025-2026, $n = 56$ semaines) :

### Baseline 1 : SARIMAX
* **Modèle** : ARIMA(3, 0, 1) avec variables exogènes.
* **Limites** : Modèle linéaire incapable de s'adapter aux accélérations exponentielles et aux dynamiques d'asymétrie typiques des virus (montées abruptes, descentes lentes).
* **Résultat** : $R^2 = 0.177$ | RMSE = 7 139 cas.

### Baseline 2 : Meta Prophet
* **Modèle** : Prophet avec régresseurs exogènes, `changepoint_prior_scale=0.5` et saisonnalité annuelle par harmoniques de Fourier.
* **Limites** : Prophet décompose les signaux en ondes sinusoïdales régulières, lissant artificiellement les pics de saturation hospitalière critiques.
* **Résultat** : $R^2 = 0.531$ | RMSE = 5 391 cas.

### Modèle Final : BiLSTM (Bidirectional LSTM)
* **Modèle** : Réseau neuronal récurrent bidirectionnel avec couche `Bidirectional(LSTM(64))`, suivi d'un `Dropout(0.2)` et d'une couche dense de décision.
* **Principe** : Analyse des séquences dans les deux sens temporels sur une fenêtre glissante de **12 semaines × 7 features** (tenseur d'entrée 3D `(batch, 12, 7)`).
* **Stratégie anti-overfitting** : Train/Test split chronologique strict (80/20), entraînement du scaler uniquement sur le train, callbacks `EarlyStopping` (patience=10) et `ReduceLROnPlateau`.
* **Résultat** : $R^2 = 0.731$ | MAE = 3 095 cas | RMSE = 4 083 cas.

---

## ⚡ 3. L'Innovation de Production : La Cascade d'IA

### Le Défi opérationnel (Le "Mur de production")
En recherche (notebook), nous avons accès au présent. Mais le lundi matin en production, la donnée officielle d'incidence de la semaine en cours ($S_0$) n'est pas encore publiée par le réseau Sentinelles (délai de 12 jours). Le modèle BiLSTM, ayant besoin de 12 semaines complètes d'incidence pour s'exécuter, refuse de prédire la semaine suivante ($S_{+1}$) sans la valeur de la semaine actuelle $S_0$.

### La Solution : Le Nowcaster MLP Delta
Nous avons développé un second modèle d'IA, le **Nowcaster**, entraîné spécifiquement à "deviner" l'incidence du présent ($S_0$) à partir des seuls signaux disponibles instantanément à latence 0 jour (Météo, Google Trends, Calendrier de la semaine en cours) et de l'inertie des 11 semaines passées.

#### Technique du Delta
1. On masque la case de l'incidence actuelle dans le tenseur : `seq[-1, 0] = 0`.
2. Le Nowcaster (MLP BiLSTM allégé) estime la **variation d'incidence** : $\Delta = inc(T) - inc(T-1)$.
3. On reconstruit l'incidence présente : $\hat{inc}(T) = inc(T-1) + \Delta$.
4. Cette valeur estimée $\hat{inc}(T)$ est **injectée** dans le tenseur d'entrée à la place du trou.
5. Le tenseur complété alimente ensuite le **Forecaster BiLSTM** pour prédire $S_{+1}$.

* **Performances du Nowcaster seul** : $R^2 = 0.892$ | RMSE = 2 633 cas | MAPE = 14.9%.

---

## 🔒 4. Robustesse Spécifique : Classification d'Alerte

Pour passer de la régression brute à une aide à la décision binaire opérationnelle, les prédictions d'incidence sont classifiées en seuil critique d'alerte Orsan (Plan Blanc) à partir du percentile 85 ($P_{85} = 29\,906$ cas/semaine) :

* **Rappel (Sensibilité)** : **100%** (0 faux négatifs, aucune crise sanitaire n'a été manquée sur l'historique de test).
* **Précision globale** : **96%**.
* **Coût asymétrique** : Le système génère 2 fausses alarmes sur 56 semaines. En santé publique, une fausse alerte coûte des heures supplémentaires de préparation, tandis qu'un faux négatif (une crise non anticipée) coûte des vies humaines. Ce compromis a été statistiquement validé.
