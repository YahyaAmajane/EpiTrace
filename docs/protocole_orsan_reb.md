# DIRECTIVE RÉGIONALE ADAPTÉE — DISPOSITIF ORSAN REB (Risque Épidémique et Biologique)
**Source :** Ministère des Solidarités et de la Santé / Santé Publique France — **Adaptation régionale : Île-de-France**
**Application :** Établissements de santé (Plan Blanc), Médecine de Ville, Officines.
**Contexte :** Gestion des tensions hospitalières liées aux Infections Respiratoires Aiguës (IRA) — Région Île-de-France (12,2 millions d'habitants).

> **Note méthodologique :** Les seuils d'incidence de ce protocole sont calibrés sur les données épidémiologiques réelles du Réseau Sentinelles pour l'Île-de-France (2021–2026, n=277 semaines). Ils sont exprimés en **nombre de cas hebdomadaires consultants** estimés pour la région. Le seuil national ORSAN (< 2 000 cas) est inapplicable à cette région dont le minimum historique est de 2 819 cas/semaine. Les quatre niveaux sont définis par les **percentiles statistiques** de la distribution observée : P50, P75, P85 — la seule variable déclencheuse est l'**incidence prévue à J+7** générée par le modèle BiLSTM Epi-Trace.

Ce document définit les actions obligatoires en fonction des prévisions d'incidence épidémique à **J+7** générées par le modèle BiLSTM Epi-Trace (R²=0.73, RMSE=4 116 cas).

---

## NIVEAU 1 : VEILLE SAISONNIÈRE (Vert)
**Déclencheur unique :** Incidence prévue **< 14 206 cas/semaine** (en dessous de la médiane historique — P50).
**Fréquence historique :** ~50% des semaines.

* **Hôpitaux :** Phase de préparation standard. Vérification de l'adéquation de l'offre de soins avec l'activité prévisionnelle. Maintien des filières d'urgences classiques. Aucune déprogrammation.
* **Pharmacies :** Gestion de stock nominale. Suivi du registre des Médicaments d'Intérêt Thérapeutique Majeur (MITM). Vérification des niveaux de paracétamol et ibuprofène en prévision de la montée de saison.
* **Médecine de Ville :** Recherche de diagnostic différentiel classique pour tout patient symptomatique. Rappel des gestes barrières en consultation.

---

## NIVEAU 2 : MISE EN TENSION ET PRÉ-ALERTE (Jaune)
**Déclencheur unique :** Incidence prévue entre **14 206 et 20 076 cas/semaine** (entre P50 et P75).
**Fréquence historique :** ~25% des semaines.

* **Hôpitaux :** Activation de la Cellule de Crise Hospitalière (CCH). Anticipation d'une augmentation de 20 à 30% des passages aux urgences. Préparation à l'ouverture de lits d'aval en médecine interne. Vérification du stock de masques FFP2 et surblouses.
* **Pharmacies :** Alerte préventive sur les tensions d'approvisionnement. Majoration de 30% des commandes d'antipyrétiques (paracétamol, ibuprofène) et d'amoxicilline. Information des patients sur les tensions potentielles.
* **Médecine de Ville :** Sensibilisation aux clusters familiaux et scolaires. Affichage obligatoire des consignes barrières en salle d'attente. Recours encouragé à la téléconsultation pour le renouvellement d'ordonnances simples et les cas non urgents.

---

## NIVEAU 3 : DÉCLENCHEMENT DU PLAN BLANC (Orange)
**Déclencheur unique :** Incidence prévue entre **20 076 et 26 866 cas/semaine** (entre P75 et P85).
**Fréquence historique :** ~10% des semaines.

* **Hôpitaux :** Déclenchement du Plan Blanc par la direction de l'établissement en coordination avec l'ARS Île-de-France. Déprogrammation progressive des interventions chirurgicales non urgentes (report à J+14 minimum). Rappel du personnel en repos sous 24h. Ouverture de lits supplémentaires en médecine interne et pneumologie. Mise en place de circuits dédiés IRA aux urgences.
* **Pharmacies :** Contingentement préfectoral. Délivrance de paracétamol limitée : 1 boîte pour patient asymptomatique, 2 boîtes maximum pour patient symptomatique (sans ordonnance). Modification possible de la durée de validité des ordonnances sur décision préfectorale. Coordination inter-officines pour les ruptures de stock.
* **Médecine de Ville :** Bascule en "Diagnostic Syndromique" : l'association toux + fièvre + contexte épidémique régional vaut diagnostic de syndrome grippal, sans test systématique. Prescription d'antiviraux (oseltamivir) autorisée sans confirmation virologique. Orientation directe vers les urgences pour toute détresse respiratoire (SpO2 < 94%).

---

## NIVEAU 4 : SATURATION RÉGIONALE — CRISE MAJEURE (Rouge)
**Déclencheur unique :** Incidence prévue **> 26 866 cas/semaine** (au-delà du 85e percentile — seuil de crise calibré sur les données IDF).
**Fréquence historique :** ~15% des semaines — correspond aux véritables semaines épidémiques de crise (ex. : pic décembre 2022 à 70 334 cas, janvier 2024–2025).

* **Hôpitaux :** Déprogrammation totale des actes non urgents (délai de report > 21 jours). Transferts inter-régionaux des patients non critiques via coordination SAMU-Centre 15. Mobilisation de la réserve sanitaire nationale. Activation du poste de commandement médical (PCM) de l'ARS. Ouverture de structures provisoires d'accueil si occupation > 110%.
* **Pharmacies :** Délivrance stricte sur ordonnance médicale pour les antibiotiques (amoxicilline, azithromycine), corticoïdes et oxygénothérapie à domicile. Dépannage d'urgence inter-officines autorisé avec traçabilité obligatoire. Approvisionnement prioritaire via la Pharmacie à Usage Intérieur (PUI) des hôpitaux de référence.
* **Médecine de Ville :** Tri strict à l'entrée des cabinets (circuit IRA dédié). Isolement immédiat de toute détresse respiratoire avec orientation SAMU. Déploiement massif de la téléconsultation pour les cas modérés (objectif : décharger 40% des consultations présentielle). Fermeture recommandée des cabinets de groupe aux consultations sans rendez-vous.

---

## ANNEXE — BASE STATISTIQUE ET CALIBRATION DES SEUILS (IDF, 2021–2026)

| Indicateur | Valeur |
|---|---|
| Minimum historique | 2 819 cas/semaine |
| Médiane (P50) — Seuil N1 vers N2 | 14 206 cas/semaine |
| 3e Quartile (P75) — Seuil N2 vers N3 | 20 076 cas/semaine |
| 85e Percentile (P85) — Seuil N3 vers N4 | 26 866 cas/semaine |
| 95e Percentile (référence extrême) | 42 213 cas/semaine |
| Maximum historique (S52-2022) | 70 334 cas/semaine |
| RMSE modèle BiLSTM (marge d'erreur) | +/- 4 116 cas |

**Justification du P85 comme seuil de crise (N4) :** Au-delà du 85e percentile, les données historiques documentent une saturation des urgences d'Île-de-France et un recours aux transferts inter-régionaux. Ce seuil correspond aux semaines de pic grippal hivernal intense, soit environ 6 à 8 semaines par an.

**Rôle des signaux précurseurs (météo, Google Trends) :** Les variables météorologiques et les Topics Google Trends (Toux r=0.84, Grippe r=0.81, Fièvre r=0.72) sont des **inputs du modèle BiLSTM**, intégrés dans la prédiction d'incidence. Ils contribuent indirectement à la décision via l'incidence prévue — ils ne constituent pas des déclencheurs autonomes de niveau d'alerte.